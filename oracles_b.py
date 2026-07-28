"""The oracles for subject B, and the sandbox they run in.

Nothing modifies the subject. Every evaluation happens on a fresh copy in a
temporary directory that is deleted immediately afterwards.

One departure from subject A's harness, declared because it changes the cost and
not the result: **all three oracles are derived from a single execution.**
Oracle B for subject B is "every Python file byte-compiles and `verify_paper.py`
runs to completion without an uncaught exception, ignoring whether its checks
pass", which is a property of the very run oracle A already performs. Oracle C
is identical to oracle B for this subject, since it produces no regenerable
figure. Running the script twice to ask two questions about the same execution
would double an eighteen-second cost for nothing.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

import taxonomy_b

HERE = os.path.dirname(os.path.abspath(__file__))
SUBJECT = os.environ.get("STASIS_SUBJECT_B") or os.path.normpath(
    os.path.join(HERE, taxonomy_b.SUBJECT))

SKIP = ("__pycache__", ".git", ".pytest_cache")

RESULT_LINE = re.compile(r"^\s*\[(PASS|FAIL)\]\s+(\S+)\s+(.*)$")
SUMMARY_LINE = re.compile(r"(\d+) checks passed, (\d+) failed, (\d+) total")


def _ignore(_directory, names):
    return [name for name in names if name in SKIP]


def make_sandbox(destination, config):
    """Copy the subject, then apply the textual ablation for `config`."""
    shutil.copytree(SUBJECT, destination, ignore=_ignore)
    if config == "full":
        return
    for relative, old, new in taxonomy_b.ABLATION_EDITS[config]:
        path = os.path.join(destination, *relative.split("/"))
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        if text.count(old) != 1:
            raise RuntimeError("ablation %r does not apply cleanly to %s (%d matches)"
                               % (config, relative, text.count(old)))
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text.replace(old, new, 1))


def apply_mutation(destination, mutant):
    path = os.path.join(destination, *mutant["path"].split("/"))
    with open(path, encoding="utf-8") as handle:
        rows = handle.read().split("\n")
    index = mutant["line"] - 1
    if mutant["old"] not in rows[index]:
        raise RuntimeError("mutant %s no longer anchors at %s:%d"
                           % (mutant["id"], mutant["path"], mutant["line"]))
    rows[index] = rows[index].replace(mutant["old"], mutant["new"], 1)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(rows))


def run_verification(directory):
    """Execute the subject's verifier and read everything the oracles need."""
    done = subprocess.run([sys.executable, "verify_paper.py"], cwd=directory,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          universal_newlines=True)
    outcome = {}
    for row in done.stdout.split("\n"):
        match = RESULT_LINE.match(row)
        if match:
            outcome["%s|%s" % (match.group(2), match.group(3).strip())] = \
                match.group(1) == "PASS"
    summary = SUMMARY_LINE.search(done.stdout)
    return dict(outcome=outcome,
                code=done.returncode,
                parsed=bool(outcome),
                completed=bool(summary),
                crashed="Traceback (most recent call last)" in done.stdout)


def compiles(directory):
    done = subprocess.run([sys.executable, "-m", "compileall", "-q", "."],
                          cwd=directory, stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)
    return done.returncode == 0


def evaluate(job):
    """Worker entry point. `job` is (mutant or None, config name)."""
    mutant, config = job
    identifier = mutant["id"] if mutant else "BASELINE"
    directory = tempfile.mkdtemp(prefix="disb_")
    try:
        sandbox = os.path.join(directory, "subject")
        make_sandbox(sandbox, config)
        if mutant is not None:
            target = os.path.join(sandbox, *mutant["path"].split("/"))
            if not os.path.exists(target):
                return (identifier, config, dict(not_applicable=True))
            apply_mutation(sandbox, mutant)
        payload = run_verification(sandbox)
        if config == "full":
            # Oracle B, and therefore oracle C, read off the same execution.
            payload["b"] = (not compiles(sandbox)) or payload["crashed"] \
                or not payload["completed"]
            payload["c"] = payload["b"]
        return (identifier, config, payload)
    except Exception as failure:                      # noqa: BLE001
        return (identifier, config,
                dict(error="%s: %s" % (type(failure).__name__, failure)))
    finally:
        shutil.rmtree(directory, ignore_errors=True)
