# Prediction · Re-measurement of both subjects after their repairs

Alexis García Hurtado · 2026

**Committed before `DECLARED_COMMIT` is moved for either subject and before any
mutant of the re-measurement is generated.** The two preregistrations that
govern the original measurements are untouched, and so are their results. This
document adds a third dated claim to the record: what the repaired subjects are
expected to score, written down while it can still be wrong.

A prediction is evidence only if its commit precedes the data. That is the whole
reason this file exists as its own commit.

## 0 · What changed in the subjects, and why

The study measured one blind spot in both packages: frozen figures and front
matter were checked for **presence** in a document rather than for presence
**where they belong**. Subject B showed it at its cleanest — every frozen figure
occurring once in `paper.tex` was caught on every edit, and every figure
occurring more than once was caught on none.

Both subjects have now been repaired, each in its own repository:

```
subject A  minimal-verified-paper          a3390860c53290271b6d06745fe252bfa7200dac
subject B  kingwen-orderings-replication   95437d30f805be447cccabb30ea54ff983741f52
```

Subject A anchors each frozen claim to the line it sits on, or freezes how many
times it is stated, and reads every front matter string out of the field,
heading or byline position it lives in. 104 checks became 109.

Subject B pins every frozen figure to the exact positions it occupies in
`paper.tex` — which lines, and how many times on each — which is stricter than
counting, because it also catches a figure that moved. Its living surfaces are
checked by structure, and the number of checks it publishes is now asserted
against the number it runs. 202 checks became 246. Its manuscript and PDF were
not touched: they are archived artefacts behind a version DOI.

## 1 · Prediction for subject A

Battery of 363, regenerated against the repaired package. Rates under oracle A.

| Class | n | measured before | predicted | why |
| --- | ---: | ---: | ---: | --- |
| `front_matter_drift` | 20 | 11 · 0.550 | **20 · 1.000** | the nine escapes were four title edits in `paper.md` (YAML block and heading), four author edits (field and byline) and one year edit in the BibTeX field; all five locations are now separate assertions |
| `manuscript_number_edited` | 31 | 28 · 0.903 | **31 · 1.000** | the three escapes were `100` in section 3, now frozen at two occurrences, and `93` in the rows for digits 0 and 4, now anchored to their rows |
| `constant_copied_to_prose` | 36 | 18 · 0.500 | **24 · 0.667** | six of the eighteen escapes insert a constant into a section that already holds a claim with that text, and the occurrence count now catches them: `1000` into sections 1, 2 and 5; `100` into 2 and 3; `0.05` into 3. The other twelve land in sections with no claim for that value and still escape |
| `derivation_written_by_hand` | 10 | 7 · 0.700 | 7 · 0.700 | nothing was done about it |
| `result_embedded_in_code` | 32 | 30 · 0.938 | 30 · 0.938 | nothing was done about it |
| `data_corrupted` | 30 | 30 · 1.000 | 30 · 1.000 | unchanged |
| `data_truncated` | 4 | 4 · 1.000 | 4 · 1.000 | unchanged |
| `permutation_no_statistical_effect` | 20 | 20 · 1.000 | 20 · 1.000 | unchanged |
| `figure_gone_stale` | 27 | 27 · 1.000 | 27 · 1.000 | unchanged |
| `figure_governing_number` | 8 | 8 · 1.000 | 8 · 1.000 | unchanged |
| `frozen_value_edited` | 31 | 31 · 1.000 | 31 · 1.000 | unchanged |
| `forbidden_phrase` | 95 | 95 · 1.000 | 95 · 1.000 | unchanged |
| `nonnumeric_text_change` | 19 | 0 · 0.000 | 0 · 0.000 | negative control |
| **total** | **363** | **309** | **327** | |

## 2 · Prediction for subject B

Battery of 176, regenerated against the repaired package. Rates under oracle A.

| Class | n | measured before | predicted | why |
| --- | ---: | ---: | ---: | --- |
| `manuscript_number_edited` | 29 | 13 · 0.448 | **29 · 1.000** | these bump a frozen figure in `paper.tex`; every edit changes that figure's positional profile, whether or not other copies survive |
| `front_matter_drift` | 23 | 12 · 0.522 | **23 · 1.000** | the eleven escapes were the byline author on the landing, five DOI edits across both living surfaces, two subtitle edits and three title edits. Every one now has a location that reads it, including the `<h1>` a reader actually sees |
| `constant_copied_to_prose` | 24 | 0 · 0.000 | **24 · 1.000** | an inference, not a measurement, and flagged as the weakest claim here: these insert a line into `paper.tex`, which shifts the line number of every frozen figure below the insertion point, and positional pinning sees that |
| `derivation_written_by_hand` | 16 | 2 · 0.125 | 2 · 0.125 | nothing was done about it. Two of these sixteen are invalid instrument mutants, disclosed in `RUNS.md`; among the fourteen valid ones the rate is 0.000 and is predicted to stay there |
| `frozen_value_edited` | 25 | 20 · 0.800 | 20 · 0.800 | unchanged mechanism, and the sampling pool is unchanged at 82 qualifying call sites, so the same sites are drawn |
| `result_embedded_in_code` | 6 | 0 · 0.000 | 0 · 0.000 | subject B has no cited-versus-computed check and did not gain one |
| `forbidden_phrase_watched` | 3 | 3 · 1.000 | 3 · 1.000 | unchanged |
| `forbidden_phrase_unwatched` | 16 | 0 · 0.000 | 0 · 0.000 | subject B still watches two phrases; the rest remain invisible by construction |
| `data_corrupted` | 20 | 20 · 1.000 | 20 · 1.000 | unchanged |
| `data_truncated` | 2 | 2 · 1.000 | 2 · 1.000 | unchanged |
| `nonnumeric_text_change` | 12 | 0 · 0.000 | 0 · 0.000 | negative control |
| **total** | **176** | **72** | **123** | |

## 3 · Changes the re-measurement requires, declared before it runs

**The subject B generator is broken by the repair and must be fixed.**
`generate_b.frozen_strings()` reads a list literal named `frozen` out of
`verify_paper.py`. That list no longer exists: it became `FROZEN_FIGURES`, a
tuple of value and positional profile. The generator must be taught to read the
new structure. This is a change to the instrument, not to any preregistration,
and it is declared here rather than made quietly at run time.

**The sampling pool is unchanged, which was checked rather than assumed.** The
two subject B classes that sample from `verify_paper.py`'s check call sites draw
from 82 qualifying sites at the old commit and 82 at the new one. The new checks
added by the repair do not qualify, because their expected argument is a name
rather than a numeric literal. The same seeded indices therefore select the same
logical sites, at shifted line numbers. Those two classes stay comparable.

**Subject B's ablation configurations still apply but no longer cover
everything.** The four textual edits in `taxonomy_b.ABLATION_EDITS` all still
match exactly once. They do not touch `section_surfaces` or
`check_published_counts`, which did not exist when they were written, so the
ablation table for the re-measurement covers less of the package than it did.
Extending it would be a change to a preregistered procedure and is not made.

**Subject A's battery regenerates unchanged in structure.** Its generation rules
search for text rather than fixed positions, and every anchor they use still
resolves.

## 4 · What would surprise me

Stated as numbers, because a prediction nobody can lose is not a prediction.

**S1 · Any class predicted at 1.000 landing below 0.95.** Both repairs are
strictly stricter than what they replaced. A class that was supposed to close
and did not means the repair does not cover the defect the study injected.

**S2 · Subject B's `constant_copied_to_prose` landing below 0.90.** This is the
weakest prediction in the document. It rests on an inference about a side effect
— that inserting a line shifts positions and positional pinning notices — which
was never tested. If it comes out low, the inference was wrong, and if it comes
out at 1.000 the class is being caught for a reason other than the defect it
models, which is worth saying out loud rather than banking.

**S3 · Subject A's `constant_copied_to_prose` landing outside 0.60 to 0.72.**
The predicted 0.667 comes from counting exactly which six of eighteen escapes
the occurrence rule now catches. Landing outside that band means the counting
was wrong.

**S4 · Any class that was at 1.000 before falling below it.** Neither repair
relaxes anything. A new escape would mean the repair broke a check that used to
work, and that would be the most important result the re-measurement could
produce.

**S5 · Either negative control moving off 0.000.** That would mean the repairs
made the packages fire on comment edits, and every other rate in the
re-measurement would have to be discounted.

**S6 · Totals outside 320 to 334 for subject A, or 116 to 130 for subject B.**

**What would not surprise me:** `derivation_written_by_hand` and
`result_embedded_in_code` staying exactly where they are in both subjects.
Nothing was done about either, and predicting movement there would be predicting
that a repair I did not make had an effect.

## 5 · What this document does not claim

It does not claim the repairs are complete. They close the blind spot the study
measured, and the study measured what its taxonomy could reach. The classes that
escaped for reasons unrelated to location — a hand-written derivation whose value
happens to be right, a result cached beside the code that computes it — are
untouched in both subjects and are predicted to escape again.

It also does not claim the two subjects are now comparable in the way section 7
of the subject B preregistration meant. Subject B still lacks mechanisms subject
A has, and criterion G0 still excludes those classes from any generalisation.
