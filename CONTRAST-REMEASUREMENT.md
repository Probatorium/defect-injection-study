# Contrast · the re-measurement against the prediction committed in 963ceb1

`PREDICTION-REMEASUREMENT.md` was committed before `DECLARED_COMMIT` was moved
for either subject and before a single mutant of this re-measurement was
generated. It has not been edited, and it will not be. This file reports what
happened against it.

```
subject A  minimal-verified-paper         e6e4250 -> a3390860c53290271b6d06745fe252bfa7200dac
subject B  kingwen-orderings-replication  73d9a77 -> 95437d30f805be447cccabb30ea54ff983741f52
seeds      20260728 (A) and 20260729 (B), unchanged
ablations  unchanged; no preregistered operationalisation was extended
```

## 1 · Subject A, class by class

| Class | before | after | predicted | detections | rate |
| --- | ---: | ---: | ---: | :-: | :-: |
| `front_matter_drift` | 11/20 · 0.550 | **20/21 · 0.952** | 20/20 · 1.000 | hit | **missed** |
| `manuscript_number_edited` | 28/31 · 0.903 | **31/31 · 1.000** | 31/31 · 1.000 | hit | hit |
| `constant_copied_to_prose` | 18/36 · 0.500 | **24/36 · 0.667** | 24/36 · 0.667 | hit | hit |
| `derivation_written_by_hand` | 7/10 · 0.700 | 7/10 · 0.700 | 7/10 · 0.700 | hit | hit |
| `result_embedded_in_code` | 30/32 · 0.938 | 30/32 · 0.938 | 30/32 · 0.938 | hit | hit |
| `frozen_value_edited` | 31/31 · 1.000 | 31/31 · 1.000 | 31/31 · 1.000 | hit | hit |
| `data_corrupted` | 30/30 · 1.000 | 30/30 · 1.000 | 30/30 · 1.000 | hit | hit |
| `data_truncated` | 4/4 · 1.000 | 4/4 · 1.000 | 4/4 · 1.000 | hit | hit |
| `permutation_no_statistical_effect` | 20/20 · 1.000 | 20/20 · 1.000 | 20/20 · 1.000 | hit | hit |
| `figure_gone_stale` | 27/27 · 1.000 | 27/27 · 1.000 | 27/27 · 1.000 | hit | hit |
| `figure_governing_number` | 8/8 · 1.000 | 8/8 · 1.000 | 8/8 · 1.000 | hit | hit |
| `forbidden_phrase` | 95/95 · 1.000 | 95/95 · 1.000 | 95/95 · 1.000 | hit | hit |
| `nonnumeric_text_change` | 0/19 · 0.000 | 0/20 · 0.000 | 0/20 · 0.000 | hit | hit |
| **total** | **309/363 · 0.851** | **327/365 · 0.896** | 327 | hit | |

**One rate prediction failed, and it is recorded as failed.**
`front_matter_drift` was predicted at 20 detections out of a battery of 20, a
rate of 1.000. The detection count is exactly 20. The rate is 0.952, because the
battery grew to 21. The cause is in section 4.

## 2 · Subject B, class by class

| Class | before | after | predicted | detections | rate |
| --- | ---: | ---: | ---: | :-: | :-: |
| `manuscript_number_edited` | 13/29 · 0.448 | **29/29 · 1.000** | 29/29 · 1.000 | hit | hit |
| `front_matter_drift` | 12/23 · 0.522 | **23/23 · 1.000** | 23/23 · 1.000 | hit | hit |
| `constant_copied_to_prose` | 0/24 · 0.000 | **24/24 · 1.000** | 24/24 · 1.000 | hit | hit |
| `frozen_value_edited` | 20/25 · 0.800 | 20/25 · 0.800 | 20/25 · 0.800 | hit | hit |
| `derivation_written_by_hand` | 2/16 · 0.125 | 2/16 · 0.125 | 2/16 · 0.125 | hit | hit |
| `result_embedded_in_code` | 0/6 · 0.000 | 0/6 · 0.000 | 0/6 · 0.000 | hit | hit |
| `forbidden_phrase_watched` | 3/3 · 1.000 | 3/3 · 1.000 | 3/3 · 1.000 | hit | hit |
| `forbidden_phrase_unwatched` | 0/16 · 0.000 | 0/16 · 0.000 | 0/16 · 0.000 | hit | hit |
| `data_corrupted` | 20/20 · 1.000 | 20/20 · 1.000 | 20/20 · 1.000 | hit | hit |
| `data_truncated` | 2/2 · 1.000 | 2/2 · 1.000 | 2/2 · 1.000 | hit | hit |
| `nonnumeric_text_change` | 0/12 · 0.000 | 0/12 · 0.000 | 0/12 · 0.000 | hit | hit |
| **total** | **72/176 · 0.409** | **123/176 · 0.699** | 123 | hit | |

Subject B's battery is identical to the published one, class by class, 176
mutants either side. The repaired generator was checked against that before
anything was run.

## 3 · The weakest prediction, and it is not counted as a win

`constant_copied_to_prose` on subject B was predicted at 1.000 and measured at
1.000. The prediction document names it as the weakest claim in the document and
states in advance what a 1.000 would mean. That sentence stands, and it is
repeated here rather than quietly dropped:

> If it comes out at 1.000 the class is being caught for a reason other than the
> defect it models, which is worth saying out loud rather than banking.

The defect this class models is a constant retyped into the prose without a
computation behind it. What actually catches all 24 is that inserting a line
into `paper.tex` shifts the line number of every frozen figure below it, and
subject B now pins those positions. The class would be caught identically if the
inserted sentence contained no number at all. **This is not evidence that
subject B detects hand-copied constants.** It is evidence that subject B detects
any edit to its archived manuscript, which is a different and narrower claim.

Subject A's version of the class did not move for that reason: its claims are
anchored by line content and by occurrence count, not by position, so an
inserted sentence is invisible unless it duplicates a value the section already
freezes. Its 0.667 is the honest measurement of the mechanism.

## 4 · The six declared surprises

| | Surprise | Materialised |
| --- | --- | :-: |
| **S1** | a class predicted at 1.000 landing below 0.95 | **no** |
| **S2** | subject B `constant_copied_to_prose` below 0.90 | **no** |
| **S3** | subject A `constant_copied_to_prose` outside 0.60 to 0.72 | **no** |
| **S4** | a class at 1.000 before falling below it | **no** |
| **S5** | either negative control moving off 0.000 | **no** |
| **S6** | totals outside 320-334 for A, or 116-130 for B | **no** |

None of the six materialised. S1 came closest and did not trigger:
`front_matter_drift` on subject A landed at 0.952, above the 0.95 line by two
hundredths, on a battery of 21.

## 5 · Every escape that persists, with its cause named

### Subject A, 38 escapes of 365

**`nonnumeric_text_change`, 20 of 20.** The negative control. Escaping is the
correct outcome; a detection here would mean the package fires on comment edits.

**`constant_copied_to_prose`, 12 of 36.** A sentence carrying a package constant
is appended to a manuscript section. Twelve of the eighteen constants land in a
section that holds no frozen claim with that text, so no occurrence count moves
and nothing objects. The twelve are distributed 2, 1, 1, 3, 2, 3 across the six
section anchors. The six that are now caught are the ones that duplicate a value
their section already freezes.

**`derivation_written_by_hand`, 3 of 10.** Unchanged from the first measurement
and unchanged in cause. `Fraction(237, 50)` in the exact statistics path: the
literals 237 and 50 are not guarded values. `degrees_of_freedom = 9` in the
analysis: below the guarding threshold of ten, by that check's stated design.
`expected = Fraction(100, 1)`: the value 100 is guarded, but the edit sits
inside `src/frozen_claims.py`, which is the one module exempt from the scan
because it is where the frozen values are allowed to live. The exemption that
makes the mechanism workable is a blind spot inside the exempt module.

**`result_embedded_in_code`, 2 of 32.** `CACHED_REPORTED_VALUE = 9` inserted
into each of the two statistics modules. Nine is below the guarding threshold.

**`front_matter_drift`, 1 of 21.** `README.md` line 83, the string `2026`. This
is the mutant that grew the battery. The line is prose written while documenting
the repair -- *"because the digits `2026` also sit inside the citation key"* --
and the enumeration rule generates one mutant per line containing the value.
Escaping is correct behaviour: a prose mention inside a code span is not a front
matter location and nothing should assert it. It counts as an escape because the
class enumeration over-generates, not because the check is weak.

### Subject B, 53 escapes of 176

**`forbidden_phrase_unwatched`, 16 of 16.** Subject B watches two strings, an em
dash in the manuscript and a pending-DOI announcement on the living surfaces.
The other phrases are invisible to it by construction. Unchanged and expected.

**`derivation_written_by_hand`, 14 of 16.** Subject B implements no
cited-versus-computed check and did not gain one. The two that are detected are
the invalid instrument mutants disclosed in `RUNS.md`; among the fourteen that
satisfy the class definition the rate is 0.000.

**`nonnumeric_text_change`, 12 of 12.** The negative control.

**`result_embedded_in_code`, 6 of 6.** No such mechanism in subject B.

**`frozen_value_edited`, 5 of 25.** A newly named cause, uniform across all
five. Every one of them targets a `check(...)` call that supplies an explicit
`ok=` argument:

```
line  452   ok=close(sd_w, 11, 2)
line  466   ok=close(mean_o, 991, 5)
line  560   ok=29.0 - 0.6 <= pair_pct[...] <= 29.4 + 0.6
line  566   ok=close(pair_pct[...], 89.7, 0.8)
line 1076   ok=close(0.035 * cells, 0.6, 0.006)
```

When `ok=` is passed, `check()` uses it as the verdict and the `paper` argument
becomes decorative: it is printed next to the reproduced value and never
compared. Editing the frozen value in such a call therefore cannot change
whether the check passes. Five of the twenty-five sampled call sites are of this
kind. The rate of 0.800 is not noise and is not a sampling artefact; it is the
proportion of subject B's checks whose published value is displayed rather than
asserted.

## 6 · What the two batteries did, and did not, hold constant

**Subject B: identical.** 176 mutants, same count in every class, same sampling
pool of 82 qualifying call sites before and after.

**Subject A: 363 became 365.** Two classes grew by one, each for a mechanical
reason, and neither was chosen:

- `nonnumeric_text_change` 19 to 20. The rule takes the first comment longer
  than twelve characters in each module. `checks/check_40_frozen_numbers.py` had
  none before it was rewritten for location anchoring, and has one now.
- `front_matter_drift` 20 to 21. The rule takes every line containing the value.
  `README.md` went from one line containing `2026` to two, the second being the
  prose that documents the repair.

Both were identified and reported before the run, while the prediction was
already committed and could still be scored against them.
