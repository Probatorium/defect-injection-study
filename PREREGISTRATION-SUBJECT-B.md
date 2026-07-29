# Preregistration · Subject B · kingwen-orderings-replication

Alexis García Hurtado · 2026

**This document is committed before the first mutant of subject B is generated
and before the second study is run.** `PREREGISTRATION.md`, which governs
subject A, is not touched by it: that document and its results stand as they
were published.

## 0 · This is not a blind experiment, and saying so is obligatory

The results for subject A are already known to whoever wrote this document. The
predictions below are therefore **informed predictions in a replication**, not
predictions made in ignorance. Each one states the rate subject A produced and
what is expected of subject B relative to it.

That weakens the evidential value of any prediction that comes true and
strengthens the value of any that fails. It is declared here rather than
discovered later.

The question this study asks is narrow: **are the measured rates a property of
the method, or of one repository?** It cannot be answered by a study that
already knows what it wants to see, so the refutation criteria in section 6 are
written as differences between subjects with a fixed margin, not as thresholds
that subject B could pass by being similar in some unspecified way.

## 1 · The subject

```
repository  theoriginaliching/kingwen-orderings-replication
commit      73d9a77cdc59ea1410ae815cbb484dc68eb752d1
baseline    202 checks, 0 failed, exit 0
runtime     18.6 s per verification (subject A: 0.72 s, a factor of 26)
files       11 tracked
```

Nothing in this study modifies it. It is pinned by the same mechanism used for
subject A: the study refuses to run unless the subject is at the declared
commit with a clean worktree.

### How subject B differs structurally from subject A

| | Subject A | Subject B |
| --- | --- | --- |
| manuscript | `paper.md`, markdown | `paper.tex`, LaTeX, plus a built `paper.pdf` |
| apparatus | 11 modules under `checks/`, discovered by listing the directory | one script, `verify_paper.py`, 1358 lines, organised as `section_*()` functions called from `main()` |
| check identity | short stable ids (`FRZ-chi_square`) | `(section, claim sentence)` pairs, verified unique across the 202 |
| surfaces | `paper.md`, `README.md`, `CITATION.bib` | `paper.tex`, `README.md`, `index.html` landing page, and the `/Title` and `/Author` metadata inside `paper.pdf` |
| bibliography | separate `CITATION.bib` | BibTeX embedded in `README.md` and `index.html` |
| figure | committed SVG, regenerated and byte-compared | none; the word "figure" in this package means a number, not an image |
| structural invariants | a gate: the run stops before any statistic | checks only; nothing aborts, though corrupted input often crashes later by accident |
| mutation study | automated, `mutate.py`, report read back by a check | three `sed` one-liners documented in the README, run once by hand, enforced by nothing |
| DOI | none yet; the package forbids any DOI-shaped string | two live DOIs, a version DOI in `paper.tex` and a concept DOI on the living surfaces, checked separately |

## 2 · Which classes apply, and which do not

Ten of the thirteen classes apply. Three do not, and the reasons are structural
rather than convenient.

### Excluded

**`figure_governing_number` — NOT APPLICABLE.** Subject B has no figure
renderer. There is no module-level constant that governs a drawing because
there is no drawing. Enumerating this class would require inventing a target.

**`figure_gone_stale` — NOT APPLICABLE.** There is no committed, regenerable
image to go stale. The only image in the repository is a logo, which no
computation produces.

**`permutation_no_statistical_effect` — NOT APPLICABLE.** In subject A the
statistic was a function of digit counts, so a permutation of the data left
every reported number unchanged and the class isolated the double derivation.
In subject B the object of study *is* an ordering, and every reported statistic
is a function of that order: inversion counts, Kendall tau, adjacent Hamming
cost. **No permutation of the input is statistically inert.** The class cannot
be constructed here. Excluding it removes the class that in subject A was caught
by mechanism 3 and by nothing else, which is noted in section 3 as part of the
double derivation problem.

### Applicable, with the re-operationalisation each one needs

**1 `manuscript_number_edited`.** Subject A: increment the final digit of a
frozen claim's literal in the markdown, anchored to the section it belongs to.
Subject B: increment the final digit of one of the **29 strings** listed in
`section_paper`'s `frozen` list, wherever it occurs in `paper.tex`. Two
substantive differences, declared: subject B checks only that a frozen string is
**present somewhere in the file**, not that it is present in the right section;
and only those 29 strings are covered, while every other number printed in the
LaTeX source is unguarded. Enumeration: exhaustive over the 29.

**2 `constant_copied_to_prose`.** Same construction: append a sentence to the
LaTeX body carrying a numeric literal lifted from the package. Subject B has
**no orphan-number scan** — nothing walks the manuscript looking for numbers
without a claim behind them. Enumeration: exhaustive over four insertion points
in `paper.tex` × six constants, three of which are frozen strings and three of
which are not.

**3 `derivation_written_by_hand`.** Same construction: replace a computed
expression in `verify_paper.py` with the literal it currently produces. Subject
B has **no cited-versus-computed check** and no scan for hard-coded results.
Enumeration: exhaustive over a declared list of derivation sites.

**6 `frozen_value_edited`.** Subject A: edit the frozen string in the claim
table. Subject B: edit the `paper` argument of a `check(...)` call, which is
where subject B keeps the value the manuscript is supposed to print.
Enumeration: sampled from the 153 call sites with the declared seed, because the
cost per run makes exhaustive enumeration of all of them expensive; the sample
size is declared in `taxonomy_b.py` and reported.

**7 `result_embedded_in_code`.** Same construction: a dead assignment carrying a
currently-correct reported value. Enumeration: exhaustive over declared
insertion points × declared values.

**8 `forbidden_phrase`.** Subject A watched 19 phrases over 5 surfaces. Subject
B watches **two things only**: `paper.tex` must contain no em dash, and
`README.md` and `index.html` must not contain the string `DOI pending`. The
enumeration is therefore split in two on purpose:
  * *watched* perturbations — an em dash into `paper.tex`, `DOI pending` into
    each of the two living surfaces;
  * *unwatched* perturbations — phrases from subject A's watch list that subject
    B does not watch, inserted into the same surfaces.
The second half measures the cost of having a two-item watch list instead of a
nineteen-item one, and is expected to escape.

**9 `front_matter_drift`.** Richer in subject B than in subject A. Fields:
title, subtitle, author, version DOI, concept DOI, BibTeX doi field. Surfaces:
`paper.tex`, `README.md`, `index.html`. Enumeration: exhaustive over field ×
surface × perturbation kind, restricted to combinations that exist.

**10 `data_corrupted`.** Subject A: change one decimal digit of pi. Subject B:
change one entry of the embedded `KING_WEN` table of 64 values. Note this is a
strictly stronger perturbation than subject A's: a changed entry breaks the
permutation property, whereas a changed digit of pi leaves the sequence
well-formed. Enumeration: sampled positions with the declared seed.

**11 `data_truncated`.** Subject A: a derivation path returns one element fewer
or one more. Subject B: the `KING_WEN` table loses or gains an entry.
Enumeration: exhaustive over the two directions.

**13 `nonnumeric_text_change`.** The negative control, unchanged in spirit: a
word altered in a source comment or in non-numeric prose. Enumeration:
exhaustive over the declared list.

## 3 · The double derivation problem, resolved here and not later

Subject A carries both derivation paths inside the package, so mechanism 3 could
be ablated by deleting the module that compares them.

Subject B does not. Its independent re-derivation lives in a **sibling
repository**, `theoriginaliching/iching-experiments`, which is not part of the
subject and is not pinned by this study. Inside `verify_paper.py` there is only
`SEED_LADDER_CONTROL`, a control re-derivation used for the conditional-null
ladder, not a comparison covering the reported figures generally. **There is no
check in subject B whose removal would constitute ablating mechanism 3.**

**Decision: mechanism 3 is EXCLUDED from subject B, not simulated.**

The reasons, in order of weight:

1. Simulating it would mean pulling in a second repository and pinning a second
   moving target. A study that depends on two external commits to reproduce is
   one that will stop reproducing sooner.
2. Anything simulated would be a mechanism this study wrote, not the mechanism
   the package ships. Measuring the marginal contribution of code that does not
   exist in the subject would be measuring this study's own invention.
3. The class that isolated mechanism 3 in subject A —
   `permutation_no_statistical_effect` — is independently inapplicable to
   subject B (section 2). Even a simulated mechanism 3 would have no class that
   isolates it.

**Consequence, declared now:** the mechanism 3 row of the comparison table reads
*not measured* for subject B. Its subject A value stands alone and **no
generalisation about mechanism 3 is supported by this study.** That is a hole in
the replication, and it is a hole created by the subject's architecture rather
than by the method.

## 4 · Oracles, re-operationalised

**Oracle A — full package.** `python verify_paper.py --quiet` on the mutated
copy. Detected when a check that passes in the matching clean baseline fails or
disappears, or the run crashes. Identical in spirit to subject A.

**Oracle B — it builds.** Subject A ran the artifact's build step,
`make_figure.py`. Subject B's build product is `paper.pdf` compiled from
`paper.tex`, **and no LaTeX toolchain is present on the measuring machine**;
`pdflatex`, `xelatex` and `latexmk` are all absent. Compiling the manuscript is
therefore not part of oracle B, and this is declared rather than silently
dropped. Oracle B for subject B is: every Python file byte-compiles, and
`verify_paper.py` runs to completion without an uncaught exception, ignoring
whether its checks pass.

**Oracle C — figures regenerate and match.** Subject B produces no regenerable
figure, so there is nothing to regenerate and nothing to compare. **Oracle C is
identical to oracle B for subject B.** Every oracle C cell for subject B is
therefore a restatement of oracle B, and the C column must not be read as
evidence about dynamic-document workflows on this subject. In subject A oracle C
detected 67 of 309; that number has no counterpart here.

## 5 · Ablation, re-operationalised

Subject A ablated a mechanism by deleting the check modules that implement it.
Subject B has no modules to delete, so a mechanism is ablated by **removing its
`section_*()` call from `main()`**, or, where a mechanism is implemented by
individual `check(...)` lines rather than a whole section, by deleting those
lines. Both are mechanical textual edits, applied to the throwaway copy.

| Mechanism | Ablatable in subject B? | How |
| --- | --- | --- |
| 1 frozen claims | **partly** | remove `section_paper()`, which is the manuscript-facing half. The value-versus-paper comparison is diffuse across every section function and cannot be removed without disabling the whole script. |
| 2 claim-to-check map | **no** | the map exists in `README.md` but no check enforces it |
| 3 double derivation | **no** | see section 3 |
| 4 mutation study | **no** | mutations are documented in the README and enforced by nothing |
| 5 structural invariants | yes | remove `section_0()` |
| 6 forbidden phrases | yes | delete the two `check(...)` lines that implement them |
| 7 cited vs computed | **no** | the mechanism is absent from subject B |
| 8 front matter | yes | remove `section_front_matter()` and `section_pdf_metadata()` |

**Declared consequence:** the ablation table for subject B has four rows, not
eight, and the mechanism 1 row measures a strictly smaller thing than subject
A's mechanism 1 row. Those two numbers are **not comparable** and will be marked
as such in the output rather than placed side by side as though they were.

## 6 · Predictions, informed by subject A

Each row states subject A's measured rate under oracle A, the prediction for
subject B, and the reason. Rates are point estimates.

| Class | A measured | B predicted | Reason |
| --- | ---: | ---: | --- |
| `manuscript_number_edited` | 0.903 | **≈ 0.90–1.00** | both packages check that frozen strings appear in the manuscript; subject B's list is explicit and short, so fewer collisions than the string coincidences that caused A's three escapes |
| `frozen_value_edited` | 1.000 | **≈ 1.00** | editing the value the check compares against makes the check fail in both architectures |
| `data_corrupted` | 1.000 | **1.00** | in subject B a corrupted entry also breaks the permutation invariant, a strictly stronger signal than in subject A |
| `data_truncated` | 1.000 | **1.00** | same |
| `front_matter_drift` | 0.550 | **> 0.550** | subject B checks more surfaces and more fields, including PDF metadata, and reads canonical strings from macros rather than searching a whole file for a substring. If it lands near 0.55 the escape is architectural rather than incidental. |
| `forbidden_phrase` (watched half) | 1.000 | **1.00** | both are substring scans over declared surfaces |
| `forbidden_phrase` (unwatched half) | not present in A | **0.00** | subject B watches two phrases; the rest are invisible to it by construction |
| `constant_copied_to_prose` | 0.500 | **0.00** | subject B has no orphan-number scan at all. Subject A's 0.500 came from having one with a string-matching limit; subject B has neither the check nor the limit. |
| `derivation_written_by_hand` | 0.700 | **0.00** | subject A caught these only through the cited-versus-computed check, which subject B does not implement |
| `result_embedded_in_code` | 0.938 | **0.00** | same reason |
| `nonnumeric_text_change` | 0.000 | **0.00** | negative control; a non-zero rate here means the harness is subject-specific |

**Three of these predictions are for zero**, and they are the informative ones:
they predict that classes subject A caught will escape subject B entirely,
because subject B does not implement the mechanism that caught them. If they
come true, the measured rates are a property of *which mechanisms a package
implements*, not of the method as an abstraction, and the paper must say so.

## 7 · Refutation criteria, expressed as differences

The unit of comparison is a class. The margin is **0.25** in absolute
difference of detection rate under oracle A. It is set that wide deliberately:
class sizes here are of the order of 20 to 30, so a 95% Wilson interval is
roughly ±0.20 wide, and a tighter margin would fire on sampling noise alone.

**G0 · Scope.** G1 applies only to classes where **both** subjects implement the
mechanism that catches them. Classes where subject B lacks the mechanism
entirely — `constant_copied_to_prose`, `derivation_written_by_hand`,
`result_embedded_in_code`, and the unwatched half of `forbidden_phrase` — are
**not tests of generalisation**. A large difference there measures a difference
in what the two packages implement, which is already known. They are reported in
the comparison table and excluded from G1.

**G1 · Per class.** For any jointly-implemented class, if
`|rate_B − rate_A| > 0.25`, the claim that that class's detection rate is a
property of the method is **refuted for that class**.

**G2 · Wholesale.** If more than half of the jointly-implemented classes breach
G1, the claim of generalisation fails for the method as a whole and not merely
class by class.

**G3 · Negative control.** If `|rate_B − rate_A| > 0.05` on
`nonnumeric_text_change`, the harness is measuring something subject-specific
and every other comparison in this study is void.

**G4 · Attribution.** If a class is caught in both subjects at similar rates but
by **different mechanisms**, the rate is reproducible while the explanation is
not. This is reported as a distinct outcome rather than folded into G1.

**Not used as criteria**, and the reasons:

- Pooled rates across the whole battery, in either subject. Battery composition
  differs between subjects by necessity, so the pooled numbers are not
  comparable even in principle.
- Oracle C comparisons, since oracle C collapses onto oracle B for subject B.
- Anything about mechanism 3, which is not measured for subject B.

## 8 · What is fixed here, and what is reported afterwards

**Fixed by this document:** class applicability and every exclusion with its
reason; the re-operationalisation of each applicable class; the resolution of the
double derivation problem; the oracle and ablation re-operationalisations; every
prediction, declared as informed; the margin of 0.25; and criteria G0 to G4.

**Reported with the results, not fixed here:** the instance count each class
yields; the sample sizes actually used, which follow from the cost per run and
will be declared in the output; the wall-clock cost; and any class that had to be
sampled more aggressively than planned, which will be stated if it happens.

If a prediction fails, the prediction is not rewritten. The failure is reported.
