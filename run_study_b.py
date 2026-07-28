#!/usr/bin/env python3
"""Run the defect injection study against subject B, and compare it with A.

    python run_study_b.py

Writes results/study_report_b.md, results/raw_results_b.tsv and
results/comparison.md. All three are pure functions of the two subjects and the
declared seeds, so re-running produces byte-identical output.

Subject A's results are read back from results/raw_results.tsv rather than
copied by hand, so the comparison cannot drift from the run that produced it.
"""

import argparse
import io
import math
import os
import statistics
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import taxonomy_b


def _parse(argv):
    parser = argparse.ArgumentParser(description="Defect injection study, subject B.")
    parser.add_argument("--subject", default=None, metavar="PATH")
    parser.add_argument("--force-commit-mismatch", action="store_true")
    return parser.parse_args(argv)


def _git(path, *args):
    done = subprocess.run(("git",) + args, cwd=path, stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL, universal_newlines=True)
    return done.returncode, done.stdout.strip()


def _pin_or_exit(path, force):
    """Same refusal rule as subject A: measure the declared commit or say so."""
    if not os.path.isdir(path):
        commit, worktree, problems = "missing", "missing", ["the subject directory does not exist"]
    else:
        code, commit = _git(path, "rev-parse", "HEAD")
        if code != 0:
            commit, worktree, problems = "not-a-git-repository", "unknown", \
                ["the subject is not a git repository"]
        else:
            _, porcelain = _git(path, "status", "--porcelain")
            worktree = "clean" if not porcelain else "dirty"
            problems = []
            if commit != taxonomy_b.DECLARED_COMMIT:
                problems.append("the subject is at %s but this study declares %s"
                                % (commit[:12], taxonomy_b.DECLARED_COMMIT[:12]))
            if worktree == "dirty":
                problems.append("the subject worktree has uncommitted changes")
    complaint = "; ".join(problems)
    if problems and not force:
        print("REFUSING TO RUN: %s" % complaint)
        print("")
        print("The rates this study publishes were measured against one commit of one")
        print("package. Publishing numbers from another under the declared commit")
        print("would be a report that lies about what it measured.")
        sys.exit(2)
    if complaint:
        print("WARNING: running unpinned: %s" % complaint)
    return dict(commit=commit, worktree=worktree, declared=taxonomy_b.DECLARED_COMMIT,
                matches=(not problems), complaint=complaint)


ARGUMENTS = _parse(sys.argv[1:])
HERE = os.path.dirname(os.path.abspath(__file__))
SUBJECT_PATH = os.path.abspath(ARGUMENTS.subject) if ARGUMENTS.subject else \
    os.path.normpath(os.path.join(HERE, taxonomy_b.SUBJECT))
os.environ["STASIS_SUBJECT_B"] = SUBJECT_PATH
PIN = _pin_or_exit(SUBJECT_PATH, ARGUMENTS.force_commit_mismatch)

import generate_b                                                  # noqa: E402
import oracles_b                                                   # noqa: E402

RESULTS = os.path.join(HERE, "results")
CONFIGS = ("full",) + taxonomy_b.MECHANISMS
Z = statistics.NormalDist().inv_cdf(0.975)


def wilson(successes, total):
    if total == 0:
        return (0.0, 0.0, 0.0)
    phat = successes / float(total)
    denominator = 1.0 + Z * Z / total
    centre = (phat + Z * Z / (2.0 * total)) / denominator
    half = (Z / denominator) * math.sqrt(phat * (1.0 - phat) / total
                                         + Z * Z / (4.0 * total * total))
    return phat, max(0.0, centre - half), min(1.0, centre + half)


def newcombe(k1, n1, k2, n2):
    """Newcombe's hybrid score interval for the difference of two proportions.

    Built from the two Wilson intervals, which is why it behaves sensibly when a
    rate sits at 0 or 1 -- and several of them do here.
    """
    if n1 == 0 or n2 == 0:
        return (0.0, 0.0, 0.0)
    p1, l1, u1 = wilson(k1, n1)
    p2, l2, u2 = wilson(k2, n2)
    delta = p1 - p2
    lower = delta - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    upper = delta + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    return delta, max(-1.0, lower), min(1.0, upper)


def detected(baseline_outcome, result):
    """Detected when a check that passed in this configuration's baseline no longer does."""
    if result.get("not_applicable") or result.get("error"):
        return None, []
    if not result["parsed"]:
        return True, ["<crash before any check ran>"]
    dead = [check for check, ok in baseline_outcome.items()
            if ok and not result["outcome"].get(check, False)]
    if not dead and not result["completed"]:
        return True, ["<run did not complete>"]
    return bool(dead), sorted(dead)


def subject_a_rates():
    """Per-class counts for subject A, read back from its own raw results."""
    path = os.path.join(RESULTS, "raw_results.tsv")
    if not os.path.exists(path):
        return {}
    rows = io.open(path, encoding="utf-8").read().strip().split("\n")[1:]
    counts = {}
    for row in rows:
        field = row.split("\t")
        cls, hit = field[1], field[4] == "1"
        total, hits = counts.get(cls, (0, 0))
        counts[cls] = (total + 1, hits + (1 if hit else 0))
    return counts


def main():
    started = time.perf_counter()
    battery = generate_b.build()
    mutants = battery.mutants
    print("battery: %d mutants, %d configurations" % (len(mutants), len(CONFIGS)))

    jobs = [(None, config) for config in CONFIGS]
    for mutant in mutants:
        for config in CONFIGS:
            jobs.append((mutant, config))
    print("jobs: %d  (each verification takes about 18.6 s)" % len(jobs))

    workers = max(2, min(12, (os.cpu_count() or 4) - 2))
    results = {}
    done_count = 0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for identifier, config, payload in pool.map(oracles_b.evaluate, jobs, chunksize=2):
            results[(identifier, config)] = payload
            done_count += 1
            if done_count % 100 == 0:
                print("  %d/%d  (%.0fs)" % (done_count, len(jobs),
                                            time.perf_counter() - started))

    errors = sorted((key, payload["error"]) for key, payload in results.items()
                    if payload.get("error"))
    not_applicable = sum(1 for p in results.values() if p.get("not_applicable"))
    integrity = dict(errors=errors, not_applicable=not_applicable, jobs=len(jobs))

    baselines = {}
    for config in CONFIGS:
        payload = results[("BASELINE", config)]
        if payload.get("error"):
            print("ABORT: baseline for %s errored: %s" % (config, payload["error"]))
            return 1
        baselines[config] = payload["outcome"]
    if any(not ok for ok in baselines["full"].values()):
        print("ABORT: the unablated baseline is not clean")
        return 1
    if results[("BASELINE", "full")].get("b"):
        print("ABORT: a baseline oracle fires on the unmutated package")
        return 1

    rows = []
    for mutant in mutants:
        verdict, dead = detected(baselines["full"], results[(mutant["id"], "full")])
        payload = results[(mutant["id"], "full")]
        ablation = {}
        for config in taxonomy_b.MECHANISMS:
            ablation[config] = detected(baselines[config],
                                        results[(mutant["id"], config)])[0]
        rows.append(dict(mutant=mutant, a=verdict, dead=dead,
                         b=payload.get("b"), c=payload.get("c"), ablation=ablation))

    write_raw(rows)
    write_report(rows, battery, PIN, integrity, len(baselines["full"]))
    write_comparison(rows)
    print("elapsed: %.0f s" % (time.perf_counter() - started))
    return 0


def write_raw(rows):
    if not os.path.isdir(RESULTS):
        os.makedirs(RESULTS)
    out = ["\t".join(("mutant_id", "class", "path", "line", "oracle_a", "oracle_b",
                      "oracle_c", "checks_killed", "killed_ids"))]
    for row in sorted(rows, key=lambda r: r["mutant"]["id"]):
        mutant = row["mutant"]
        out.append("\t".join((
            mutant["id"], mutant["cls"], mutant["path"], str(mutant["line"]),
            "1" if row["a"] else "0", "1" if row["b"] else "0",
            "1" if row["c"] else "0", str(len(row["dead"])), " ~ ".join(row["dead"]))))
    with io.open(os.path.join(RESULTS, "raw_results_b.tsv"), "w",
                 encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(out) + "\n")


def _rate_row(label, successes, total):
    phat, low, high = wilson(successes, total)
    return "| %s | %d | %d | %.3f | %.3f - %.3f |" % (label, successes, total, phat, low, high)


def write_report(rows, battery, pin, integrity, baseline_checks):
    classes = sorted(set(row["mutant"]["cls"] for row in rows))
    lines = []
    add = lines.append
    add("# Defect injection study · Subject B · kingwen-orderings-replication")
    add("")
    if not pin["matches"]:
        add("> **UNPINNED RUN.** %s" % pin["complaint"])
        add("")
    add("Generated by `run_study_b.py`. Predictions were committed in")
    add("`PREREGISTRATION-SUBJECT-B.md` before this battery was generated, and")
    add("were informed by subject A's results, which is declared there.")
    add("")
    add("```")
    add("SUBJECT_COMMIT_DECLARED: %s" % pin["declared"])
    add("SUBJECT_COMMIT_FOUND: %s" % pin["commit"])
    add("SUBJECT_WORKTREE: %s" % pin["worktree"])
    add("SUBJECT_PINNED: %s" % ("yes" if pin["matches"] else "NO"))
    add("SUBJECT_BASELINE_CHECKS: %d" % baseline_checks)
    add("SEED: %d" % taxonomy_b.SEED)
    add("MUTANTS: %d" % len(rows))
    add("CLASSES: %d" % len(classes))
    add("CONFIGURATIONS: %d" % len(CONFIGS))
    add("JOBS: %d" % integrity["jobs"])
    add("JOBS_ERRORED: %d" % len(integrity["errors"]))
    add("JOBS_NOT_APPLICABLE: %d" % integrity["not_applicable"])
    add("SAMPLE_FROZEN_VALUE_EDITED: %d" % taxonomy_b.SAMPLE_FROZEN_VALUE_EDITED)
    add("SAMPLE_DERIVATION_CHECK_SITES: %d" % taxonomy_b.SAMPLE_DERIVATION_CHECK_SITES)
    add("SAMPLE_DATA_CORRUPTED: %d" % taxonomy_b.SAMPLE_DATA_CORRUPTED)
    add("```")
    add("")
    add("## Classes excluded from subject B")
    add("")
    for cls, reason in sorted(taxonomy_b.EXCLUDED_CLASSES.items()):
        add("- `%s` — %s" % (cls, reason))
    add("")
    add("## 1 · Battery composition")
    add("")
    add("| Class | Mutants |")
    add("| --- | ---: |")
    for cls in classes:
        add("| `%s` | %d |" % (cls, sum(1 for r in rows if r["mutant"]["cls"] == cls)))
    add("| **total** | **%d** |" % len(rows))
    add("")
    add("## 2 · Detection rate by class and oracle")
    add("")
    add("Wilson score intervals at 95%. Oracles B and C are identical for this")
    add("subject, which produces no regenerable figure; both are read off the same")
    add("execution as oracle A.")
    add("")
    for key, name in (("a", "Oracle A · full package"),
                      ("b", "Oracle B · it builds"),
                      ("c", "Oracle C · identical to B for this subject")):
        add("### %s" % name)
        add("")
        add("| Class | detected | n | rate | 95% Wilson |")
        add("| --- | ---: | ---: | ---: | --- |")
        for cls in classes:
            subset = [r for r in rows if r["mutant"]["cls"] == cls and r[key] is not None]
            add(_rate_row("`%s`" % cls, sum(1 for r in subset if r[key]), len(subset)))
        scored = [r for r in rows if r[key] is not None]
        add(_rate_row("**pooled (not a citable quantity)**",
                      sum(1 for r in scored if r[key]), len(scored)))
        add("")
    add("## 3 · Ablation")
    add("")
    add("Only four of the eight mechanisms are ablatable in subject B. The others")
    add("are listed below with the reason, and read *not measured* rather than zero.")
    add("")
    add("| Mechanism | scored | detected without it | new escapes |")
    add("| --- | ---: | ---: | ---: |")
    for mechanism in taxonomy_b.MECHANISMS:
        scored = [r for r in rows if r["ablation"][mechanism] is not None and r["a"] is not None]
        still = sum(1 for r in scored if r["ablation"][mechanism])
        new_escapes = sum(1 for r in scored if r["a"] and not r["ablation"][mechanism])
        flag = " *" if mechanism in taxonomy_b.NOT_COMPARABLE_ABLATION else ""
        add("| %s%s | %d | %d | **%d** |" % (mechanism, flag, len(scored), still, new_escapes))
    add("")
    add("`*` ablated only in its manuscript-facing half; **not comparable** with")
    add("subject A's mechanism 1 row.")
    add("")
    add("**The two ablations are not disjoint, and this was not foreseen.** In")
    add("subject B the function `section_paper()` carries two checks: the frozen")
    add("strings must appear in `paper.tex` (mechanism 1) and the manuscript must")
    add("contain no em dash (mechanism 6). Removing that function to ablate")
    add("mechanism 1 therefore removes one of mechanism 6's two checks as well.")
    add("The measured baselines make the overlap exact: ablating mechanism 1 drops")
    add("2 checks and ablating mechanism 6 drops 3, sharing the em-dash check.")
    add("The preregistered operationalisation was kept rather than rewritten after")
    add("the fact; what is reported instead is that mechanism 1's ablation figure")
    add("for subject B is contaminated by mechanism 6 to the extent of one check.")
    add("Subject A had no such overlap, because there each mechanism owned its own")
    add("module. This is a property of a single-script architecture, not of the")
    add("method.")
    add("")
    for mechanism, reason in sorted(taxonomy_b.NOT_ABLATABLE.items()):
        add("- **%s** — not measured: %s" % (mechanism, reason))
    add("")
    add("## 4 · Per-mutant raw data")
    add("")
    add("`results/raw_results_b.tsv`.")
    add("")
    with io.open(os.path.join(RESULTS, "study_report_b.md"), "w",
                 encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")


#: How a subject B class name maps onto subject A's. Declared rather than
#: guessed, because the forbidden-phrase class was deliberately split in two.
CLASS_MAP = {
    "manuscript_number_edited": "manuscript_number_edited",
    "constant_copied_to_prose": "constant_copied_to_prose",
    "derivation_written_by_hand": "derivation_written_by_hand",
    "frozen_value_edited": "frozen_value_edited",
    "result_embedded_in_code": "result_embedded_in_code",
    "forbidden_phrase_watched": "forbidden_phrase",
    "forbidden_phrase_unwatched": None,
    "front_matter_drift": "front_matter_drift",
    "data_corrupted": "data_corrupted",
    "data_truncated": "data_truncated",
    "nonnumeric_text_change": "nonnumeric_text_change",
}


def write_comparison(rows):
    a_counts = subject_a_rates()
    lines = []
    add = lines.append
    add("# Subject A against subject B, class by class")
    add("")
    add("Subject A's counts are read back from `results/raw_results.tsv`, not")
    add("copied by hand. Differences are B minus A, with Newcombe's hybrid score")
    add("interval at 95%, which is built from the two Wilson intervals and stays")
    add("sensible when a rate sits at 0 or 1, as several do here.")
    add("")
    add("`G1` is the preregistered criterion: for a class both subjects implement,")
    add("a difference larger than %.2f refutes the claim that its detection rate is"
        % taxonomy_b.G1_MARGIN)
    add("a property of the method. `G0` excludes from G1 the classes where subject B")
    add("has no corresponding mechanism at all.")
    add("")
    add("| Class | n A | rate A | n B | rate B | diff (B−A) | 95% Newcombe | in G1 | verdict |")
    add("| --- | ---: | ---: | ---: | ---: | ---: | --- | :-: | --- |")
    breaches, jointly = [], []
    for cls_b in sorted(CLASS_MAP):
        subset = [r for r in rows if r["mutant"]["cls"] == cls_b and r["a"] is not None]
        if not subset:
            continue
        n_b = len(subset)
        k_b = sum(1 for r in subset if r["a"])
        cls_a = CLASS_MAP[cls_b]
        if cls_a is None or cls_a not in a_counts:
            add("| `%s` | — | — | %d | %.3f | — | — | no | no counterpart in subject A |"
                % (cls_b, n_b, k_b / float(n_b)))
            continue
        n_a, k_a = a_counts[cls_a]
        delta, low, high = newcombe(k_b, n_b, k_a, n_a)
        in_g1 = cls_b not in taxonomy_b.NOT_JOINTLY_IMPLEMENTED
        if in_g1:
            jointly.append(cls_b)
            breached = abs(delta) > taxonomy_b.G1_MARGIN
            if breached:
                breaches.append((cls_b, delta))
            verdict = "**G1 BREACHED**" if breached else "within margin"
        else:
            verdict = "G0: mechanism absent in B"
        add("| `%s` | %d | %.3f | %d | %.3f | %+.3f | %.3f to %.3f | %s | %s |"
            % (cls_b, n_a, k_a / float(n_a), n_b, k_b / float(n_b), delta, low, high,
               "yes" if in_g1 else "no", verdict))
    for cls_a, reason in sorted(taxonomy_b.EXCLUDED_CLASSES.items()):
        if cls_a in a_counts:
            n_a, k_a = a_counts[cls_a]
            add("| `%s` | %d | %.3f | — | — | — | — | no | not applicable to B: %s |"
                % (cls_a, n_a, k_a / float(n_a), reason))
    add("")
    add("## Preregistered criteria")
    add("")
    add("- **G1** per class, margin %.2f: **%s**%s"
        % (taxonomy_b.G1_MARGIN, "BREACHED for %d class(es)" % len(breaches) if breaches
           else "not breached",
           (" — " + ", ".join("%s (%+.3f)" % (c, d) for c, d in breaches)) if breaches else ""))
    add("- **G2** more than half of the %d jointly-implemented classes breach G1: **%s** "
        "(%d of %d)" % (len(jointly),
                        "MET" if jointly and len(breaches) > len(jointly) / 2.0 else "not met",
                        len(breaches), len(jointly)))
    control = [r for r in rows if r["mutant"]["cls"] == "nonnumeric_text_change"
               and r["a"] is not None]
    rate_b = sum(1 for r in control if r["a"]) / float(len(control)) if control else 0.0
    n_a, k_a = a_counts.get("nonnumeric_text_change", (0, 0))
    rate_a = k_a / float(n_a) if n_a else 0.0
    add("- **G3** negative control differs by more than %.2f: **%s** — A %.3f, B %.3f"
        % (taxonomy_b.G3_MARGIN,
           "MET" if abs(rate_b - rate_a) > taxonomy_b.G3_MARGIN else "not met",
           rate_a, rate_b))
    add("- **G4** same rate reached by different mechanisms: see the mechanism")
    add("  attribution in each subject's own report; mechanism 3 is not measured")
    add("  for subject B and no generalisation about it is supported.")
    add("")
    with io.open(os.path.join(RESULTS, "comparison.md"), "w",
                 encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    sys.exit(main())
