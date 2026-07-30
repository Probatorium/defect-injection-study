# Defect injection study of the Stasis apparatus

A measurement instrument, not a paper. It takes the package at
`../minimal-verified-paper` as its subject, injects defects into throwaway
copies of it by rule, and measures what each of three oracles catches.

**Nothing here modifies the subject.** Every mutation is applied to a copy in a
temporary directory that is deleted immediately afterwards.

## Reproduce it in three steps

```
git clone https://github.com/Probatorium/minimal-verified-paper.git
git clone https://github.com/Probatorium/defect-injection-study.git
cd minimal-verified-paper && git checkout a339086 && cd ../defect-injection-study && python run_study.py
```

Clone the two repositories as siblings, put the subject at the commit this study
declares, and run one command. Python 3 standard library, no third-party
packages, no network. About ten minutes on twelve cores: 363 mutants evaluated
under nine configurations plus two baseline oracles is 3640 sandboxed runs.

## Where the subject is, and which commit it must be at

The path is not fixed in the source. In order of precedence:

```
python run_study.py --subject /path/to/minimal-verified-paper
STASIS_SUBJECT=/path/to/minimal-verified-paper python run_study.py
python run_study.py            # default: ../minimal-verified-paper, a sibling clone
```

**The study refuses to run against the wrong subject.** Every rate it reports
was measured against one commit of one package, declared as `DECLARED_COMMIT` in
`subject.py`. If the subject is at a different commit, is not a git repository,
or has uncommitted changes, the study stops and says so rather than producing a
report that would read as though it had measured the declared state. A dirty
worktree counts: the files on disk are then not the files that commit names.

```
python run_study.py --force-commit-mismatch
```

overrides the refusal. It hides nothing: the report is stamped with the commit
actually found, `SUBJECT_PINNED` reads `NO`, and a warning block is prepended
saying the numbers do not describe the declared subject.

```
python generate.py     print the battery composition without running anything
```

## Order of work, and why it matters

1. `PREREGISTRATION.md` and `taxonomy.py` were committed **before the first
   mutant was generated**. They fix the classes, the operational definitions,
   the enumeration rules, the seed, the three oracles, a prediction for every
   class, and five numeric refutation criteria.
2. The battery was generated and the study was run afterwards.
3. Predictions that failed are reported as failed. The preregistration has not
   been edited, and will not be.

The git history of this directory is the evidence for that order.

## What is measured

**Thirteen defect classes**, eleven enumerated exhaustively over the subject and
two sampled with the declared seed. Four are predicted to escape wholly or in
part, including a negative control predicted to be caught at zero by every
oracle. A battery in which everything is caught cannot distinguish a method that
works from a battery chosen to flatter it.

**Three oracles.**

| Oracle | Definition | Detected when |
| --- | --- | --- |
| A · full package | `python verify.py` on the mutated copy | a check that passes in the matching clean baseline fails or never runs; a crash counts |
| B · it builds | every module byte-compiles and `make_figure.py` exits 0 | either step fails |
| C · figures regenerate and match | oracle B, then the regenerated figure is compared to the committed one | B fires, or the bytes differ |

Oracle C contains oracle B by construction, and is deliberately more generous
than a real dynamic-document workflow, which regenerates a figure without ever
comparing it against the previous one.

**Ablation.** Each of the eight mechanisms is disabled by deleting the check
modules that implement it, and the whole battery is re-run under oracle A. What
is ablated is the mechanism, not the code it inspects: removing the double
derivation removes the comparison between the two paths, not the second path.

## Files

```
PREREGISTRATION.md    predictions and refutation criteria, committed first
taxonomy.py           the thirteen classes, the seed, the ablation map
subject.py            where the subject is, and the commit it must be at
generate.py           rule-based, seeded generation of the battery
oracles.py            the three oracles and the sandbox they run in
run_study.py          the single command
results/
  study_report.md     every rate, matrix and criterion verdict
  raw_results.tsv     one row per mutant, with the ids of every check that died
```

`subject.py` is deliberately separate from `taxonomy.py`. That module was
committed as part of the preregistration, and the preregistration is evidence
about what was predicted before any data existed. Adding machinery to it
afterwards would weaken that evidence for no gain.

## Reading the numbers

Per-class rates carry Wilson score intervals at 95%. **The pooled rate across
the whole battery is not a meaningful quantity**: it depends on how many
instances each class contributes, which is a design choice of this study rather
than a property of the method. It is printed for completeness and should not be
quoted as a headline.

`JOBS_NOT_APPLICABLE` counts (mutant, configuration) pairs in which the mutant's
target file does not exist because the ablation under test removes it. A defect
cannot be injected into a file a configuration does not contain, so those pairs
are excluded from that mechanism's ablation counts rather than scored as
escapes. Jobs that raise are reported and excluded on the same principle: a
harness failure silently counted as a non-detection would bias every rate
downwards.

## Reproducibility

The report is a pure function of the subject package and the declared seed.
Nothing in `results/` carries a timestamp, a sandbox path or a wall-clock
measurement, so two runs over the same subject produce byte-identical files.
Work is spread across processes, which cannot affect the result: jobs are
independent, each runs in its own directory, and results are keyed and sorted
before anything is aggregated.

The subject commit is recorded at the top of the report, and the study refuses
to run against any other unless explicitly forced. A result measured against one
commit says nothing about another: if the blind spots this study found are ever
fixed in the subject, these numbers stop describing it and the battery has to be
re-run against the new commit.
