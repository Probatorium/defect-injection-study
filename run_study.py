#!/usr/bin/env python3
"""Run the defect injection study. One command, standard library only, no network.

    python run_study.py

Writes results/study_report.md and results/raw_results.tsv. Both are pure
functions of the subject package and the declared seed, so re-running produces
byte-identical output; nothing in either file carries a timestamp, a path from
the sandbox, or a wall-clock measurement.

Work is spread across processes because the battery costs a few thousand
subprocess runs. Parallelism cannot affect the result: every job is independent,
runs in its own temporary directory, and the results are keyed and then sorted
before anything is aggregated.
"""

import argparse
import io
import math
import os
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import phase5
import subject as subject_module
import taxonomy


def _parse(argv):
    parser = argparse.ArgumentParser(
        description="Defect injection study of the Stasis apparatus.")
    parser.add_argument("--subject", default=None, metavar="PATH",
                        help="path to the subject package; overrides the "
                             "STASIS_SUBJECT environment variable and the "
                             "default sibling directory")
    parser.add_argument("--force-commit-mismatch", action="store_true",
                        help="run even though the subject is not at the declared "
                             "commit, or its worktree is dirty; the report is "
                             "stamped with what was actually found and marked "
                             "as unpinned")
    return parser.parse_args(argv)


def _pin_or_exit(path, force):
    """Verify the subject before anything else happens, and stop if it is wrong.

    This runs at import time, ahead of `generate` and `oracles`, for two
    reasons. Those modules settle on a subject path when they are imported, and
    `generate` imports the subject's own source: pointing the study at something
    that is not the subject would otherwise fail with an import error from deep
    inside, instead of a sentence saying what is wrong.

    Returns the pin record stamped into the report. Exits 2 if the study must
    not run.
    """
    may_run, commit, worktree, complaint = subject_module.check(path, force)
    if not may_run:
        print("REFUSING TO RUN: %s" % complaint)
        print("")
        print("The rates this study publishes were measured against one commit of")
        print("one package. Running the same battery against a different one and")
        print("reporting it under the declared commit would be a report that lies")
        print("about what it measured.")
        print("")
        print(subject_module.how_to_fix())
        sys.exit(2)
    if complaint:
        print("WARNING: running unpinned because --force-commit-mismatch was given")
        print("         %s" % complaint)
    return dict(commit=commit, worktree=worktree,
                declared=subject_module.DECLARED_COMMIT,
                matches=(commit == subject_module.DECLARED_COMMIT
                         and worktree == "clean"),
                forced=bool(complaint), complaint=complaint)


#: Resolved and verified before `generate` and `oracles` are imported. Exporting
#: the path through the environment is what carries it to the worker processes,
#: which are spawned rather than forked and so re-import those modules.
ARGUMENTS = _parse(sys.argv[1:])
SUBJECT_PATH = subject_module.resolve(ARGUMENTS.subject)
subject_module.export(SUBJECT_PATH)
PIN = _pin_or_exit(SUBJECT_PATH, ARGUMENTS.force_commit_mismatch)

import generate                                                   # noqa: E402
import oracles                                                    # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")

CONFIGS = ("full",) + taxonomy.MECHANISMS + tuple(phase5.EXTRA_ABLATION)

Z = statistics.NormalDist().inv_cdf(0.975)


def wilson(successes, total):
    """Wilson score interval for a binomial proportion, 95%."""
    if total == 0:
        return (0.0, 0.0, 0.0)
    phat = successes / float(total)
    denominator = 1.0 + Z * Z / total
    centre = (phat + Z * Z / (2.0 * total)) / denominator
    half = (Z / denominator) * math.sqrt(phat * (1.0 - phat) / total
                                         + Z * Z / (4.0 * total * total))
    return phat, max(0.0, centre - half), min(1.0, centre + half)




def detected_by_a(baseline_outcome, result):
    """A mutant is detected when a check that passed in the baseline no longer does.

    Absence counts: a check that never ran because a gate stopped the suite is a
    check the mutant prevented from passing. A crash with no parseable output
    counts too, and is recorded separately.

    Returns (verdict, dead ids). The verdict is None when the pair is not
    applicable or the job errored; None is excluded from every rate rather than
    counted as an escape.
    """
    if result.get("not_applicable") or result.get("error"):
        return None, []
    if not result["parsed"]:
        return True, ["<crash>"]
    dead = [check for check, ok in baseline_outcome.items()
            if ok and not result["outcome"].get(check, False)]
    return bool(dead), sorted(dead)


def main():
    started = time.perf_counter()
    pin = PIN
    battery = generate.build()
    mutants = battery.mutants
    print("battery: %d mutants, %d configurations" % (len(mutants), len(CONFIGS)))

    jobs = [("A", None, config) for config in CONFIGS]
    jobs.append(("BC", None, "full"))
    for mutant in mutants:
        for config in CONFIGS:
            jobs.append(("A", mutant, config))
        jobs.append(("BC", mutant, "full"))
    print("jobs: %d" % len(jobs))

    workers = max(2, min(12, (os.cpu_count() or 4) - 2))
    print("workers: %d" % workers)
    results = {}
    done_count = 0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for kind, mutant_id, config, payload in pool.map(oracles.evaluate, jobs,
                                                         chunksize=4):
            results[(kind, mutant_id, config)] = payload
            done_count += 1
            if done_count % 250 == 0:
                print("  %d/%d  (%.0fs)" % (done_count, len(jobs),
                                            time.perf_counter() - started))

    # ---- harness integrity ----------------------------------------------
    errors = sorted((key, payload["error"]) for key, payload in results.items()
                    if payload.get("error"))
    not_applicable = sum(1 for payload in results.values()
                         if payload.get("not_applicable"))
    integrity = dict(errors=errors, not_applicable=not_applicable,
                     jobs=len(jobs))
    if errors:
        print("WARNING: %d jobs errored; they are excluded from every rate" % len(errors))
        for key, message in errors[:5]:
            print("   %s -> %s" % (key, message))

    # ---- baselines -------------------------------------------------------
    baseline_a = {}
    for config in CONFIGS:
        payload = results[("A", "BASELINE", config)]
        if payload.get("error"):
            print("ABORT: the baseline for %s errored: %s" % (config, payload["error"]))
            return 1
        baseline_a[config] = payload["outcome"]
    baseline_bc = results[("BC", "BASELINE", "full")]

    clean_failures = sorted(check for check, ok in baseline_a["full"].items() if not ok)
    if clean_failures:
        print("ABORT: the unablated baseline is not clean: %s" % ", ".join(clean_failures))
        return 1
    if baseline_bc["b"] or baseline_bc["c"]:
        print("ABORT: a baseline oracle fires on the unmutated package")
        return 1

    # ---- per mutant ------------------------------------------------------
    rows = []
    for mutant in mutants:
        full_detected, dead = detected_by_a(baseline_a["full"],
                                            results[("A", mutant["id"], "full")])
        bc = results[("BC", mutant["id"], "full")]
        ablation = {}
        for config in CONFIGS[1:]:
            ablated_detected, _ = detected_by_a(
                baseline_a[config], results[("A", mutant["id"], config)])
            ablation[config] = ablated_detected
        # results is keyed by (kind, mutant id, config); the gate measurement
        # reads how many checks each run actually produced.
        gate = results.get(("A", mutant["id"], "5 structural invariants"), {})
        rows.append(dict(mutant=mutant, a=full_detected, dead=dead,
                         b=bc.get("b"), c=bc.get("c"), ablation=ablation,
                         run_full=len(results[("A", mutant["id"], "full")].get("outcome", {})),
                         run_nogate=(None if (gate.get("not_applicable")
                                             or gate.get("error"))
                                     else len(gate.get("outcome", {})))))

    write_raw(rows)
    write_report(rows, battery, pin, integrity)
    print("elapsed: %.0f s" % (time.perf_counter() - started))
    return 0


#: The manuscript whose text the `manuscript_occurrences` column counts against.
MANUSCRIPT = "paper.md"


def manuscript_occurrences(target):
    """How many times a mutant's target string occurs in the subject's manuscript.

    Published because the analysis used it and readers could not re-derive it.
    A rate can be checked from the oracle columns alone, but the cross-tabulation
    of "appears once" against "appears more than once" cannot, and that
    cross-tabulation is the causal explanation of subject B's G1 breach.

    Defined for every mutant, not only manuscript ones: for a mutant that edits
    source code the count is usually zero, and saying zero is more useful than
    leaving a blank that a reader has to interpret.
    """
    text = manuscript_occurrences.cache
    if text is None:
        with io.open(os.path.join(oracles.SUBJECT, MANUSCRIPT), encoding="utf-8") as fh:
            text = fh.read()
        manuscript_occurrences.cache = text
    return text.count(target)


manuscript_occurrences.cache = None


def write_raw(rows):
    if not os.path.isdir(RESULTS):
        os.makedirs(RESULTS)
    out = ["\t".join(("mutant_id", "class", "path", "line", "oracle_a",
                      "oracle_b", "oracle_c", "checks_killed",
                      "target_string", "manuscript_occurrences",
                      "checks_run", "killed_ids"))]
    for row in sorted(rows, key=lambda r: r["mutant"]["id"]):
        mutant = row["mutant"]
        target = mutant["old"].replace("\t", " ").replace("\n", "\\n")
        out.append("\t".join((
            mutant["id"], mutant["cls"], mutant["path"], str(mutant["line"]),
            "1" if row["a"] else "0", "1" if row["b"] else "0",
            "1" if row["c"] else "0", str(len(row["dead"])),
            target, str(manuscript_occurrences(mutant["old"])),
            str(row.get("run_full", 0)), ",".join(row["dead"]))))
    with io.open(os.path.join(RESULTS, "raw_results.tsv"), "w",
                 encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(out) + "\n")


def _rate(label, successes, total):
    phat, low, high = wilson(successes, total)
    return "| %s | %d | %d | %.3f | %.3f - %.3f |" % (label, successes, total, phat, low, high)


def write_report(rows, battery, pin, integrity):
    classes = sorted(set(row["mutant"]["cls"] for row in rows))
    lines = []
    add = lines.append

    add("# Defect injection study of the Stasis apparatus")
    add("")
    if not pin["matches"]:
        add("> **UNPINNED RUN. These numbers do not describe the declared subject.**")
        add(">")
        add("> This report was produced with `--force-commit-mismatch`, against a")
        add("> subject that is not the one the study declares: %s." % pin["complaint"])
        add("> Every rate below belongs to the commit stamped as")
        add("> `SUBJECT_COMMIT_FOUND`, not to `SUBJECT_COMMIT_DECLARED`.")
        add("")
    add("Generated by `run_study.py`. Every number below is produced by the run;")
    add("nothing is entered by hand. The predictions this is measured against were")
    add("committed in `PREREGISTRATION.md` before the battery was generated.")
    add("")
    add("```")
    add("SUBJECT_COMMIT_DECLARED: %s" % pin["declared"])
    add("SUBJECT_COMMIT_FOUND: %s" % pin["commit"])
    add("SUBJECT_WORKTREE: %s" % pin["worktree"])
    add("SUBJECT_PINNED: %s" % ("yes" if pin["matches"] else "NO"))
    add("SEED: %d" % taxonomy.SEED)
    add("MUTANTS: %d" % len(rows))
    add("CLASSES: %d" % len(classes))
    add("CONFIGURATIONS: %d" % len(CONFIGS))
    add("SAMPLE_DATA_CORRUPTED: %d" % generate.SAMPLE_DATA_CORRUPTED)
    add("SAMPLE_PERMUTATION: %d" % generate.SAMPLE_PERMUTATION)
    add("SILENT_CANDIDATES_REJECTED: %d" % len(generate.REJECTED_SILENT_CANDIDATES))
    add("REJECTED_DUPLICATES: %d" % battery.rejected_duplicates)
    add("REJECTED_UNANCHORED: %d" % battery.rejected_unanchored)
    add("JOBS: %d" % integrity["jobs"])
    add("JOBS_ERRORED: %d" % len(integrity["errors"]))
    add("JOBS_NOT_APPLICABLE: %d" % integrity["not_applicable"])
    add("```")
    add("")
    add("`JOBS_NOT_APPLICABLE` counts (mutant, configuration) pairs in which the")
    add("mutant's target file does not exist because the ablation under test")
    add("removes it. A defect cannot be injected into a file the configuration")
    add("does not contain, so those pairs are excluded from that mechanism's")
    add("ablation counts rather than being scored as escapes. They affect only")
    add("the negative control class, which is the only class that targets check")
    add("modules.")
    add("")

    # ---- battery composition
    add("## 1 · Battery composition")
    add("")
    add("| Class | Mutants | Enumeration |")
    add("| --- | ---: | --- |")
    for cls in classes:
        n = sum(1 for row in rows if row["mutant"]["cls"] == cls)
        kind = "sampled" if cls in ("data_corrupted",
                                    "permutation_no_statistical_effect") else "exhaustive"
        add("| `%s` | %d | %s |" % (cls, n, kind))
    add("| **total** | **%d** | |" % len(rows))
    add("")

    # ---- detection by class and oracle
    add("## 2 · Detection rate by class and oracle")
    add("")
    add("Wilson score intervals at 95%. `n` is the number of mutants in the class.")
    add("")
    for oracle_key, oracle_name in (("a", "Oracle A · full package"),
                                    ("b", "Oracle B · it builds"),
                                    ("c", "Oracle C · figures regenerate and match")):
        add("### %s" % oracle_name)
        add("")
        add("| Class | detected | n | rate | 95% Wilson |")
        add("| --- | ---: | ---: | ---: | --- |")
        for cls in classes:
            subset = [row for row in rows
                      if row["mutant"]["cls"] == cls and row[oracle_key] is not None]
            hits = sum(1 for row in subset if row[oracle_key])
            add(_rate("`%s`" % cls, hits, len(subset)))
        scored = [row for row in rows if row[oracle_key] is not None]
        hits = sum(1 for row in scored if row[oracle_key])
        add(_rate("**all classes pooled**", hits, len(scored)))
        add("")

    # ---- mechanism against class
    add("## 3 · Mechanism against class")
    add("")
    add("Cell = number of mutants of that class for which at least one check")
    add("belonging to that mechanism failed. A mutant can appear in several")
    add("columns, so rows do not sum to the class size.")
    add("")
    mechanisms = list(taxonomy.MECHANISMS) + ["9 suite self-description"]
    add("| Class | n | " + " | ".join(m.split(" ", 1)[0] for m in mechanisms) + " |")
    add("| --- | ---: | " + " | ".join("---:" for _ in mechanisms) + " |")
    for cls in classes:
        subset = [row for row in rows if row["mutant"]["cls"] == cls]
        cells = []
        for mechanism in mechanisms:
            hits = sum(1 for row in subset
                       if any(taxonomy.mechanism_of(check) == mechanism
                              for check in row["dead"]))
            cells.append(str(hits))
        add("| `%s` | %d | %s |" % (cls, len(subset), " | ".join(cells)))
    add("")
    add("Legend: " + "; ".join(mechanisms))
    add("")

    # ---- ablation
    add("## 4 · Ablation")
    add("")
    add("Each mechanism is disabled by removing the check modules that implement")
    add("it, and the whole battery is re-run under oracle A. `new escapes` counts")
    add("mutants detected by the full package and no longer detected without that")
    add("mechanism: its measured marginal contribution over this battery.")
    add("")
    add("| Mechanism | scored | detected without it | new escapes | share of scored |")
    add("| --- | ---: | ---: | ---: | ---: |")
    ablation_summary = {}
    for mechanism in CONFIGS[1:]:
        scored = [row for row in rows if row["ablation"][mechanism] is not None
                  and row["a"] is not None]
        still = sum(1 for row in scored if row["ablation"][mechanism])
        new_escapes = sum(1 for row in scored
                          if row["a"] and not row["ablation"][mechanism])
        ablation_summary[mechanism] = new_escapes
        add("| %s | %d | %d | **%d** | %.3f |"
            % (mechanism, len(scored), still, new_escapes,
               new_escapes / float(len(scored)) if scored else 0.0))
    add("")
    add("Classes contributing the new escapes, per mechanism:")
    add("")
    for mechanism in CONFIGS[1:]:
        lost = {}
        for row in rows:
            if row["a"] and row["ablation"][mechanism] is False:
                lost[row["mutant"]["cls"]] = lost.get(row["mutant"]["cls"], 0) + 1
        detail = ", ".join("`%s` %d" % (cls, lost[cls]) for cls in sorted(lost)) or "none"
        add("- **%s**: %s" % (mechanism, detail))
    add("")

    # ---- blind spots
    add("## 5 · Escape rates, highest first")
    add("")
    add("| Class | escaped | n | escape rate | 95% Wilson |")
    add("| --- | ---: | ---: | ---: | --- |")
    ordered = []
    for cls in classes:
        subset = [row for row in rows
                  if row["mutant"]["cls"] == cls and row["a"] is not None]
        escaped = sum(1 for row in subset if not row["a"])
        ordered.append((escaped / float(len(subset)), cls, escaped, len(subset)))
    for _rate_value, cls, escaped, total in sorted(ordered, reverse=True):
        add(_rate("`%s`" % cls, escaped, total))
    add("")

    # ---- preregistered criteria
    add("## 6 · Preregistered refutation criteria")
    add("")
    add("Evaluated mechanically against the thresholds fixed in `PREREGISTRATION.md`.")
    add("")
    predicted_detected = ("manuscript_number_edited", "figure_governing_number",
                          "figure_gone_stale", "frozen_value_edited",
                          "forbidden_phrase", "front_matter_drift",
                          "data_corrupted", "data_truncated",
                          "permutation_no_statistical_effect")
    scored_a = [row for row in rows if row["a"] is not None]
    f1_breaches = []
    for cls in predicted_detected:
        subset = [row for row in scored_a if row["mutant"]["cls"] == cls]
        if not subset:
            continue
        escape = sum(1 for row in subset if not row["a"]) / float(len(subset))
        if escape > 0.10:
            f1_breaches.append("%s at %.3f" % (cls, escape))
    add("- **F1** a class predicted detected escapes more than 0.10: **%s**%s"
        % ("MET" if f1_breaches else "not met",
           (" — " + "; ".join(f1_breaches)) if f1_breaches else ""))

    a_hits = sum(1 for row in rows if row["a"])
    b_hits = sum(1 for row in rows if row["b"])
    c_hits = sum(1 for row in rows if row["c"])
    add("- **harness** %d of %d jobs errored; %d were not applicable"
        % (len(integrity["errors"]), integrity["jobs"], integrity["not_applicable"]))
    ratio_b = b_hits / float(a_hits) if a_hits else 0.0
    ratio_c = c_hits / float(a_hits) if a_hits else 0.0
    add("- **F2** a baseline reaches 0.90 of the full package: **%s** — "
        "oracle B %d/%d = %.3f, oracle C %d/%d = %.3f"
        % ("MET" if max(ratio_b, ratio_c) >= 0.90 else "not met",
           b_hits, a_hits, ratio_b, c_hits, a_hits, ratio_c))

    zero_contribution = [m for m in CONFIGS[1:] if ablation_summary[m] == 0]
    add("- **F3** a mechanism shows zero new escapes when ablated: **%s**%s"
        % ("MET" if zero_contribution else "not met",
           (" — " + ", ".join(zero_contribution)) if zero_contribution else ""))

    control = [row for row in scored_a if row["mutant"]["cls"] == "nonnumeric_text_change"]
    control_rate = sum(1 for row in control if row["a"]) / float(len(control)) if control else 0.0
    add("- **F4** the negative control is detected above 0.05: **%s** — %.3f"
        % ("MET" if control_rate > 0.05 else "not met", control_rate))

    high = 0
    for cls in classes:
        subset = [row for row in scored_a if row["mutant"]["cls"] == cls]
        if subset and sum(1 for row in subset if row["a"]) / float(len(subset)) > 0.90:
            high += 1
    add("- **F5** fewer than four classes exceed 0.90 detection: **%s** — %d classes do"
        % ("MET" if high < 4 else "not met", high))
    add("")

    add("## 6b · The gate, measured as position of failure rather than detection")
    add("")
    add("Mechanism 5 adds no detections; it decides where a run stops. For every")
    add("mutant, how many checks actually executed under the unablated package and")
    add("under the package with the structural invariants removed.")
    add("")
    groups = {}
    for r in rows:
        groups.setdefault((r.get("run_full", 0), r.get("run_nogate", 0)), []).append(r)
    add("| Checks that ran, with the gate | without it | Mutants | Classes |")
    add("| ---: | ---: | ---: | --- |")
    for key in sorted(groups, key=lambda k: (k[0], -1 if k[1] is None else k[1]),
                      reverse=True):
        members = groups[key]
        classes = sorted(set(m["mutant"]["cls"] for m in members))
        add("| %d | %s | %d | %s |"
            % (key[0], "not applicable" if key[1] is None else key[1], len(members),
               ", ".join("`%s`" % c for c in classes[:4])
               + (" and %d more" % (len(classes) - 4) if len(classes) > 4 else "")))
    add("")
    # A pair whose target file the ablation deleted is not a crash: nothing ran
    # because nothing could be injected. Those are excluded rather than counted
    # as evidence for the gate, which would overstate it by one mutant.
    crashed = [r for r in rows if r.get("run_nogate") == 0 and r.get("run_full", 0) > 0]
    if crashed:
        add("**Removing the gate does not move the failure later; it removes the")
        add("failure report altogether.** For %d mutants the unablated package stops"
            % len(crashed))
        add("after %d checks and names the invariant that failed, while the same"
            % crashed[0]["run_full"])
        add("input without the gate produces no parseable check output at all: the")
        add("run raises before any check reports. The gate's contribution is not")
        add("that it catches something nothing else catches. It is that it converts")
        add("an uncaught crash into a named structural failure, after a bounded")
        add("number of checks.")
        add("")
    add("## 7 · Per-mutant raw data")
    add("")
    add("`results/raw_results.tsv`, one row per mutant: class, target file and")
    add("line, the three oracle verdicts, and the ids of every check that died.")
    add("")

    with io.open(os.path.join(RESULTS, "study_report.md"), "w",
                 encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    sys.exit(main())
