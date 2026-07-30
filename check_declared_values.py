#!/usr/bin/env python3
"""
check_declared_values.py - the subject commit, tied across every surface that states it.

WHY THIS EXISTS. The commit that pins the subject was declared in `subject.py`
and again in the README, with nothing tying them. They drifted. A stranger
following the README would have checked out the wrong commit, hit this study's
refusal, and concluded that the package does not run.

That is **M1 in its pure form**: a value stated twice with no executable
comparison between the statements. It is the failure this whole line of work
exists to make impossible, and the mechanism was absent from it. The author of
the mechanism and the author of the failure are the same person.

THREE THINGS THIS CHECKS, and the third is the one that was missing.

  1. AGREEMENT. Every live surface states the same commit.
  2. PRESENCE. Every live surface is DECLARED, not discovered, so a surface that
     stops carrying the value fails instead of being quietly skipped. That is
     "presence is not location" applied to surfaces: a check that only compares
     the surfaces it happens to find passes happily once one is deleted.
  3. USABILITY. The pinned commit must actually CONTAIN the files the
     instructions tell the reader to run. The second failure of pass 08 was
     exactly this: `codecheck_run.py` was added to the subject AFTER the pinned
     commit, so the pin named a tree in which the instruction was impossible.
     Explaining that in prose is the wrong repair when the next reader is a
     stranger following instructions literally.

HISTORICAL SURFACES ARE NOT SYNCHRONISED, and that distinction is load-bearing.
`RUNS.md`, the contrast files and the prediction files record WHICH COMMIT WAS
MEASURED. Updating them to match a new pin would falsify the record. They are
declared below so that they are visibly excluded rather than silently missed.

EVERY FAILURE MESSAGE NAMES A REMEDY. A correct rejection whose message does not
tell the reader what to do produces the same outcome as a broken package, and
here that matters more than usual: a codechecker RECORDS but does not FIX, so an
opaque refusal turns that virtue into a false negative.

Usage:
    python check_declared_values.py
"""

import io
import os
import re
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SUJETO = os.path.normpath(os.path.join(AQUI, "..", "minimal-verified-paper"))

#: Live surfaces: (file, regex capturing the commit, what the surface is for).
#: Declared, not discovered. A surface that stops matching is a failure.
SUPERFICIES = (
    ("subject.py", r'DECLARED_COMMIT\s*=\s*"([0-9a-f]{40})"',
     "the authority. Everything else must agree with this"),
    ("README.md", r'git checkout ([0-9a-f]{7,40})',
     "the instruction a stranger follows first"),
    ("CODECHECK-ISSUE.md", r'git checkout ([0-9a-f]{7,40})',
     "the instruction inside the issue draft"),
    ("CODECHECK-ISSUE.md", r'The issue pins `([0-9a-f]{7,40})`',
     "the prose in the issue draft that states the pin"),
)

#: Files the instructions tell the reader to run inside the subject at the
#: pinned commit. The pinned tree must contain them.
EXIGIDOS_EN_EL_SUJETO = ("codecheck_run.py", "verify.py", "mutate.py")

#: Numbers stated in prose that are ALSO computed into the report from the
#: evidence. Same duplication as the commit, in a different costume, and found
#: the same way: by looking rather than by trusting.
#: (label, regex over README.md, key in results/study_report.md)
CIFRAS = (
    ("mutants", r"([0-9][0-9,]*) mutants evaluated", "MUTANTS"),
    ("sandboxed runs", r"is ([0-9][0-9,]*) sandboxed runs", "JOBS"),
)

#: Historical records of what was measured. NEVER synchronised: updating them
#: would falsify the record. Declared so the exclusion is visible.
HISTORICAS = (
    ("RUNS.md", "every run, with the subject commit it actually used"),
    ("CONTRAST-PHASE5.md", "a contrast computed at a specific subject commit"),
    ("CONTRAST-REMEASUREMENT.md", "records the move from one commit to another"),
    ("PREDICTION-REMEASUREMENT.md", "a preregistration, frozen by definition"),
    ("CODECHECK-ISSUE.md, annex", "records the drift that motivated this check"),
)


def git_sujeto(*args):
    try:
        p = subprocess.run(["git", "-C", SUJETO] + list(args),
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p.returncode, p.stdout.decode("utf-8", "replace").strip()
    except Exception as exc:
        return 1, str(exc)


def main():
    print("DECLARED VALUES: the subject commit, across every surface that states it")
    print("")
    fallos = []
    vistos = []

    for fichero, patron, para_que in SUPERFICIES:
        ruta = os.path.join(AQUI, fichero)
        if not os.path.exists(ruta):
            fallos.append("%s is a declared surface and does not exist. REMEDY: "
                          "restore it, or remove it from SUPERFICIES in this file "
                          "if the surface is genuinely gone" % fichero)
            continue
        texto = io.open(ruta, encoding="utf-8").read()
        hallados = re.findall(patron, texto)
        if not hallados:
            fallos.append("%s no longer states the subject commit (pattern %r). A "
                          "surface that stops carrying the value must fail, not be "
                          "skipped. REMEDY: restore the statement, or drop the "
                          "surface from SUPERFICIES deliberately"
                          % (fichero, patron))
            continue
        for h in hallados:
            vistos.append((fichero, h, para_que))

    autoridad = None
    for f, h, _ in vistos:
        if f == "subject.py":
            autoridad = h
    if autoridad is None:
        fallos.append("subject.py does not declare DECLARED_COMMIT, so there is no "
                      "authority to compare against. REMEDY: set DECLARED_COMMIT "
                      "in subject.py")
    else:
        print("  authority, subject.py DECLARED_COMMIT: %s" % autoridad)
        print("")
        print("  live surfaces:")
        for f, h, para_que in vistos:
            ok = autoridad.startswith(h)
            print("    %-22s %-42s %s" % (f, h, "agrees" if ok else "DISAGREES"))
            if not ok:
                fallos.append("%s states %r and the authority is %r. A stranger "
                              "following this surface would check out the wrong "
                              "tree and hit a refusal that reads like a broken "
                              "package. REMEDY: change %s to %s"
                              % (f, h, autoridad, f, autoridad[:len(h)]))

    print("")
    if not os.path.isdir(SUJETO):
        fallos.append("the subject is not a sibling directory at %s, so the pinned "
                      "commit cannot be inspected. REMEDY: clone "
                      "minimal-verified-paper next to this repository" % SUJETO)
    elif autoridad:
        print("  the pinned tree must contain what the instructions run:")
        for rel in EXIGIDOS_EN_EL_SUJETO:
            rc, _ = git_sujeto("cat-file", "-e", "%s:%s" % (autoridad, rel))
            print("    %-22s %s" % (rel, "present at the pin" if rc == 0
                                    else "ABSENT AT THE PIN"))
            if rc != 0:
                fallos.append("the pinned commit %s does not contain %s, which the "
                              "instructions tell the reader to run. The pin names a "
                              "tree in which the instruction is impossible. REMEDY: "
                              "advance DECLARED_COMMIT to a commit that contains "
                              "it, and re-run the study against that commit"
                              % (autoridad[:12], rel))

    print("")
    informe = os.path.join(AQUI, "results", "study_report.md")
    if not os.path.exists(informe):
        fallos.append("results/study_report.md does not exist, so the numbers "
                      "stated in the README are tied to nothing. REMEDY: run "
                      "`python run_study.py`")
    else:
        texto = io.open(informe, encoding="utf-8").read()
        readme = io.open(os.path.join(AQUI, "README.md"), encoding="utf-8").read()
        print("  numbers stated in prose AND computed from the evidence:")
        for etiqueta, patron, clave in CIFRAS:
            m = re.search(patron, readme)
            r = re.search(r"^%s:\s*([0-9]+)\s*$" % re.escape(clave), texto, re.M)
            dicho = m.group(1).replace(",", "") if m else None
            medido = r.group(1) if r else None
            estado = ("agrees" if dicho == medido
                      else "DISAGREES" if (dicho and medido) else "MISSING")
            print("    %-16s README %-8s report %-8s %s"
                  % (etiqueta, dicho or "absent", medido or "absent", estado))
            if dicho is None:
                fallos.append("the README no longer states the number of %s. A "
                              "surface that stops carrying the value must fail. "
                              "REMEDY: restore the sentence, or drop the entry from "
                              "CIFRAS deliberately" % etiqueta)
            elif medido is None:
                fallos.append("results/study_report.md does not report %s, so the "
                              "README's number is tied to nothing. REMEDY: check "
                              "that run_study.py still emits %s" % (clave, clave))
            elif dicho != medido:
                fallos.append("the README says %s %s and the report computed from "
                              "the evidence says %s. A codechecker reads the README "
                              "first and would meet this on their first run. "
                              "REMEDY: change the README to %s, never the report"
                              % (etiqueta, dicho, medido, medido))

    print("")
    print("  historical surfaces, NOT synchronised, declared so the exclusion is visible:")
    for f, para_que in HISTORICAS:
        print("    %-30s %s" % (f, para_que))
    print("    Updating any of these to match a new pin would falsify the record.")

    print("")
    if fallos:
        print("FAIL: %d" % len(fallos))
        for f in fallos:
            print("   X %s" % f)
        return 1
    print("OK: %d live surface(s) agree with the authority, and the pinned tree "
          "contains" % len(vistos))
    print("    every file the instructions run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
