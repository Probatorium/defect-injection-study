"""The three oracles, and the sandbox they run in.

Nothing here writes to the subject package. Every evaluation happens on a fresh
copy in a temporary directory that is deleted immediately afterwards.
"""

import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

import taxonomy

HERE = os.path.dirname(os.path.abspath(__file__))
SUBJECT = os.path.normpath(os.path.join(HERE, taxonomy.SUBJECT))
FIGURE = os.path.join("figures", "digit_frequencies.svg")

#: Never copied into a sandbox.
SKIP = ("__pycache__", ".git", ".pytest_cache")

REPORT_LINE = re.compile(r"^(PASS|FAIL) (\S+)$")


def _ignore(_directory, names):
    return [name for name in names if name in SKIP]


def make_sandbox(destination, ablated_modules=()):
    """Copy the subject, then remove the check modules of an ablated mechanism.

    Ablation is done by deleting files: `verify.py` discovers its checks by
    listing the directory, so a module that is not there is a mechanism that is
    not enforced. Nothing else in the package is touched, which is why the
    ablated baseline is measured separately rather than assumed to be clean.
    """
    shutil.copytree(SUBJECT, destination, ignore=_ignore)
    for name in ablated_modules:
        target = os.path.join(destination, "checks", name)
        if os.path.exists(target):
            os.remove(target)


def apply_mutation(destination, mutant):
    """Apply one line-anchored substitution. Raises if the anchor is gone."""
    path = os.path.join(destination, *mutant["path"].split("/"))
    with io.open(path, encoding="utf-8") as handle:
        text = handle.read()
    rows = text.split("\n")
    index = mutant["line"] - 1
    if mutant["old"] not in rows[index]:
        raise RuntimeError("mutant %s no longer anchors at %s:%d"
                           % (mutant["id"], mutant["path"], mutant["line"]))
    rows[index] = rows[index].replace(mutant["old"], mutant["new"], 1)
    with io.open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(rows))


def oracle_a(directory):
    """The full package. Returns (outcome per check id, exit code, parsed?)."""
    done = subprocess.run([sys.executable, "verify.py", "--report"],
                          cwd=directory, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, universal_newlines=True)
    outcome = {}
    for row in done.stdout.split("\n"):
        match = REPORT_LINE.match(row.strip())
        if match:
            outcome[match.group(2)] = match.group(1) == "PASS"
    return outcome, done.returncode, bool(outcome)


def oracle_b_and_c(directory):
    """The two baselines, evaluated in one pass because C contains B.

    B: every module byte-compiles and the artifact's build step exits cleanly.
    C: B, and the regenerated figure is byte-identical to the committed one.
    """
    figure_path = os.path.join(directory, FIGURE)
    with io.open(figure_path, encoding="utf-8") as handle:
        committed = handle.read()

    compiled = subprocess.run([sys.executable, "-m", "compileall", "-q", "."],
                              cwd=directory, stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
    built = subprocess.run([sys.executable, "make_figure.py"], cwd=directory,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    b_detected = compiled.returncode != 0 or built.returncode != 0

    if b_detected:
        return True, True
    with io.open(figure_path, encoding="utf-8") as handle:
        regenerated = handle.read()
    return False, regenerated != committed


def evaluate(job):
    """Worker entry point. `job` is (kind, mutant or None, config name).

    Two payloads are not results and are marked so that the aggregation can
    exclude them rather than silently score them as escapes:

    `not_applicable`  the mutant's target file does not exist in this
                      configuration. This happens when a defect is injected into
                      a check module and the ablation under test is the one that
                      removes that module: the defect cannot exist in a package
                      that does not contain the file. Such pairs are excluded
                      from that mechanism's ablation counts, and the exclusion is
                      reported.
    `error`           the job raised. Reported rather than dropped, because a
                      harness failure silently counted as a non-detection would
                      bias every rate downwards.
    """
    kind, mutant, config = job
    identifier = mutant["id"] if mutant else "BASELINE"
    ablated = () if config == "full" else taxonomy.ABLATION_MODULES[config]
    directory = tempfile.mkdtemp(prefix="dis_")
    try:
        sandbox = os.path.join(directory, "subject")
        make_sandbox(sandbox, ablated)
        if mutant is not None:
            target = os.path.join(sandbox, *mutant["path"].split("/"))
            if not os.path.exists(target):
                return (kind, identifier, config, dict(not_applicable=True))
            apply_mutation(sandbox, mutant)
        if kind == "A":
            outcome, code, parsed = oracle_a(sandbox)
            return (kind, identifier, config,
                    dict(outcome=outcome, code=code, parsed=parsed))
        detected_b, detected_c = oracle_b_and_c(sandbox)
        return (kind, identifier, config, dict(b=detected_b, c=detected_c))
    except Exception as failure:                      # noqa: BLE001
        return (kind, identifier, config,
                dict(error="%s: %s" % (type(failure).__name__, failure)))
    finally:
        shutil.rmtree(directory, ignore_errors=True)
