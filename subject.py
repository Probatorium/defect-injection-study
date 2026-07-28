"""Locating the subject package, and refusing to measure the wrong one.

Two separate concerns live here.

**Where the subject is.** Not fixed in the source. It comes from `--subject` on
the command line, else from the `STASIS_SUBJECT` environment variable, else from
the default declared in `taxonomy.py`, which assumes the two repositories are
cloned as siblings. The resolved path is exported through the environment so
that worker processes inherit it: they are spawned, not forked, so they re-import
this module and must be able to find the same subject.

**Which commit the subject is at.** Every rate this study reports was measured
against one specific commit of one specific package. Run the same battery
against a different commit and the numbers change, but the report would still
read as though it had measured the declared one. That is a report that lies
about what it measured, so the study refuses to start.

`--force-commit-mismatch` overrides the refusal. It does not hide anything: the
report is then stamped with the commit actually found and carries a warning
block at the top, so a forced run can never be mistaken for a pinned one.

This file is deliberately separate from `taxonomy.py`. That module was committed
as part of the preregistration, and the preregistration is evidence about what
was predicted before the data existed. Adding machinery to it afterwards would
weaken that evidence for no gain.
"""

import os
import subprocess

import taxonomy

#: Environment variable that carries the resolved subject path to worker
#: processes.
ENV_VAR = "STASIS_SUBJECT"

#: The commit of the subject package that this study's published numbers were
#: measured against. Update it only together with a full re-run.
DECLARED_COMMIT = "e6e4250a18397976c5a266cb132707228fff5247"

HERE = os.path.dirname(os.path.abspath(__file__))


def default_path():
    return os.path.normpath(os.path.join(HERE, taxonomy.SUBJECT))


def resolve(explicit=None):
    """Resolve the subject path: command line, then environment, then default."""
    if explicit:
        return os.path.abspath(os.path.expanduser(explicit))
    from_environment = os.environ.get(ENV_VAR)
    if from_environment:
        return os.path.abspath(os.path.expanduser(from_environment))
    return default_path()


def export(path):
    """Make the resolved path visible to spawned worker processes."""
    os.environ[ENV_VAR] = path


def _git(path, *args):
    done = subprocess.run(("git",) + args, cwd=path, stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL, universal_newlines=True)
    return done.returncode, done.stdout.strip()


def inspect(path):
    """Return (commit, worktree state) for the subject, or ('unknown', ...)."""
    if not os.path.isdir(path):
        return "missing", "missing"
    code, commit = _git(path, "rev-parse", "HEAD")
    if code != 0:
        return "not-a-git-repository", "unknown"
    code, porcelain = _git(path, "status", "--porcelain")
    if code != 0:
        return commit, "unknown"
    return commit, ("clean" if not porcelain else "dirty")


def check(path, force=False):
    """Decide whether the study may run against the subject at `path`.

    Returns (may_run, commit, worktree, complaint). A dirty worktree at the
    right commit is still not the declared state: the files on disk are not the
    files the commit names, so measuring them would misreport the subject.
    """
    commit, worktree = inspect(path)
    problems = []
    if commit == "missing":
        problems.append("the subject directory does not exist at the resolved path")
    elif commit == "not-a-git-repository":
        problems.append("the subject is not a git repository, so its commit cannot be pinned")
    elif commit != DECLARED_COMMIT:
        problems.append("the subject is at %s but this study declares %s"
                        % (commit[:12], DECLARED_COMMIT[:12]))
    if worktree == "dirty":
        problems.append("the subject worktree has uncommitted changes, so the files on "
                        "disk are not the files that commit names")
    if not problems:
        return True, commit, worktree, ""
    complaint = "; ".join(problems)
    return bool(force), commit, worktree, complaint


def how_to_fix():
    return ("Put the subject at the declared commit:\n"
            "    cd %s && git checkout %s\n"
            "or point the study elsewhere with --subject PATH, or override the\n"
            "refusal with --force-commit-mismatch, which stamps the report with\n"
            "the commit actually found and marks it as unpinned."
            % (taxonomy.SUBJECT, DECLARED_COMMIT[:12]))
