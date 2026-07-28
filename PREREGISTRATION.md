# Preregistration · Defect injection study of the Stasis apparatus

Alexis García Hurtado · 2026

**This document is committed before the first mutant is generated and before the
study is run.** It states the taxonomy, a prediction for every class, which
classes the baselines are also expected to catch, and the numeric results that
would count as refuting the usefulness of the method.

If a prediction fails, the prediction is not rewritten. The failure is reported.
A preregistration that is edited after seeing the data is not a preregistration.

---

## 0 · Design

**Subject.** The package at `../minimal-verified-paper`, at whatever commit is
recorded in the results. Nothing in this study modifies it: every mutation is
applied to a throwaway copy in a temporary directory.

**Seed.** `20260728`, declared in `taxonomy.py` and used for every sampling
decision. Enumeration is exhaustive wherever the cost allows; where it does not,
the sampling rule and its size are declared per class in `taxonomy.py` and
reported with the results.

**Three oracles**, each applied to the same battery:

| Oracle | Operational definition | Detected when |
| --- | --- | --- |
| **A · full package** | `python verify.py` on the mutated copy | at least one check that passes in the corresponding clean baseline fails or is never reached; a crash counts as detection |
| **B · it builds** | every module byte-compiles and `python make_figure.py` exits 0 | either step fails |
| **C · figures regenerate and match** | oracle B, then the regenerated figure is compared against the committed one | oracle B detects, or the bytes differ |

Oracle C contains oracle B by construction. This is stated rather than hidden:
C cannot detect fewer defects than B, so any comparison against C is a
comparison against the stronger of the two baselines.

Oracle C is deliberately generous to the baseline. A real dynamic-document
workflow regenerates the figure and never compares it against a previous
version, so it would not notice a stale figure at all. Giving the baseline the
comparison it would not normally perform makes the contrast with the full
package harder to obtain, which is the direction an honest experiment should
lean.

**Ablation.** Each of the eight mechanisms is disabled by removing the check
modules that implement it from the copy, and the whole battery is re-run under
oracle A. What is ablated is the mechanism, not the code it inspects: ablating
the double derivation removes the comparison between the two paths, not the
second path.

**Aggregate rates are not a criterion.** The overall detection rate over the
whole battery depends on how many instances each class contributes, and that is
a design choice, not a property of the method. Per-class rates are the result;
the aggregate is reported only for completeness.

---

## 1 · Taxonomy and per-class predictions

Twelve classes. Four of them are predicted to escape wholly or in part. A study
in which every class is caught cannot distinguish a method that works from a
battery that was chosen to flatter it.

### 1 · `manuscript_number_edited`

A numeric literal reported in `paper.md` is changed to a neighbouring value by
incrementing its final digit. The computation is untouched.

*Enumeration:* exhaustive over the frozen claims.

**Prediction: DETECTED, at or near 100%.** Two independent checks should fire:
the frozen-claim check finds the expected string missing from its section, and
the coverage check finds a numeric literal no claim covers. This is the defect
the method exists for, and a failure here would be a failure of the core claim.

### 2 · `constant_copied_to_prose`

A sentence carrying a numeric literal lifted from a package constant is appended
to a manuscript section. The value is correct; it was typed rather than derived.

*Enumeration:* exhaustive over six manuscript sections × six constants, three of
which are also the text of some frozen claim and three of which are not.

**Prediction: SPLIT, near 50%.** Detection should occur exactly when the copied
value is not the text of any frozen claim. The coverage check matches by string
and cannot know what role a number plays in a sentence, so a value that
coincides with an existing claim text should pass unchallenged. The subject
package documents this limit in `check_50`; this class measures it.

### 3 · `derivation_written_by_hand`

A function that computes a reported quantity is replaced by a return of the
literal value it currently produces. Correct today, and no longer following the
data.

*Enumeration:* exhaustive over a declared list of derivation sites.

**Prediction: SPLIT, and lower than class 2.** Only the cited-versus-computed
check can see this, because every reported value is still correct: the frozen
claims pass, and the double derivation still agrees since the hand-written value
equals what the other path computes. That check ignores integers below ten by
design, so a hand-written degrees-of-freedom should escape and a hand-written
`4.74` should not. This is the class most likely to embarrass the method, and it
is included for that reason.

### 4 · `figure_governing_number`

A module-level constant in the figure renderer is changed. No number in the
manuscript moves.

*Enumeration:* exhaustive over the module-level numeric constants of `src/figure.py`.

**Prediction: DETECTED at 100%** by the byte comparison of the committed figure.

### 5 · `figure_gone_stale`

A numeric text node inside the committed SVG is altered, as if the analysis had
moved on and the image had not been regenerated.

*Enumeration:* exhaustive over the numeric text nodes of the committed figure.

**Prediction: DETECTED at 100%** by the byte comparison.

### 6 · `frozen_value_edited`

The frozen string of a claim in `src/frozen_claims.py` is changed. The
manuscript is untouched.

*Enumeration:* exhaustive over the frozen claims.

**Prediction: DETECTED at or near 100%.** The mirror image of class 1: the
computed value no longer renders to the frozen string, and the manuscript now
carries a literal that no claim covers.

### 7 · `result_embedded_in_code`

A dead assignment carrying a currently-correct reported value is inserted into a
source module. Nothing reads it; it is a copy waiting to drift.

*Enumeration:* exhaustive over declared modules × declared values, half of the
values below the guarding threshold.

**Prediction: SPLIT, close to the proportion of guarded values in the
enumeration.** Detection by the cited-versus-computed check for guarded values;
escape for small integers, by that check's stated design.

### 8 · `forbidden_phrase`

One phrase from the watch list is appended to one watched surface.

*Enumeration:* exhaustive over watch list × watched surfaces.

**Prediction: DETECTED at 100%.** The check is a substring scan over exactly
these surfaces; anything less than 100% would be a defect in the study, not in
the method.

### 9 · `front_matter_drift`

Title, author or year altered on exactly one of the three surfaces that must
agree.

*Enumeration:* exhaustive over field × surface × perturbation kind.

**Prediction: DETECTED at 100%** by exact string comparison.

### 10 · `data_corrupted`

One digit of one derivation path is changed.

*Enumeration:* sampled positions, declared seed, because exhaustive enumeration
would multiply the battery by a thousand.

**Prediction: DETECTED at 100%** by the comparison between the two derivation
paths, and additionally by the published anchor when the position falls inside
the cited prefix.

### 11 · `data_truncated`

A derivation path returns one element fewer or one more than declared.

*Enumeration:* exhaustive over two paths × two directions.

**Prediction: DETECTED at 100%**, at the structural gate, before any statistic
exists. The number of checks killed should be small and the number never reached
should be large.

### 12 · `nonnumeric_text_change`

A word is altered in a source comment, or a non-numeric sentence is altered in
the manuscript or the README. No number, no claim, no watched phrase.

*Enumeration:* exhaustive over source modules carrying comments, plus a declared
list of prose lines.

**Prediction: NOT DETECTED, at 0%, by any oracle.** This is the negative
control. A method that flags this class is reporting noise, and its detection
rates elsewhere would have to be discounted accordingly.

### 13 · `permutation_no_statistical_effect`

Two elements of one derivation path are swapped. Every count, every statistic
and every p-value is unchanged.

*Enumeration:* sampled position pairs, declared seed, restricted to pairs whose
digits differ.

**Prediction: DETECTED, but by exactly one mechanism.** Only the comparison
between the two derivation paths can see it. It is invisible to every statistic
in the paper, and correctly so: the test reported there is a function of the
counts alone. Swaps falling inside the cited prefix or at the first two
positions should additionally trip the anchor or the structural invariants,
which is a property of where the sample lands and not of the class.

*(Numbering note: the taxonomy carries twelve classes in the order declared in
`taxonomy.py`; classes 12 and 13 are listed here in the order above.)*

---

## 2 · Where the baselines are expected to detect

Stated in advance so that the contrast cannot be claimed after the fact.

| Class | Oracle B expected | Oracle C expected |
| --- | --- | --- |
| `figure_governing_number` | no | **yes** |
| `figure_gone_stale` | no | **yes** |
| `data_corrupted` | no | **yes**, the counts move and the figure with them |
| `data_truncated` | no | **partly** — only when the truncated path is the one the figure is built from |
| every other class | no | no |

Both baselines are expected to detect nothing at all in classes 1, 2, 3, 6, 7,
8, 9, 12 and 13. If a baseline detects anything in the negative control, the
study harness is faulty and the run is void.

---

## 3 · What would refute the usefulness of the method

Each criterion is a number fixed now. If any of them is met, it is reported as
met, in the abstract, and not explained away.

**F1 · A class predicted DETECTED escapes more than 10% of its instances under
the full package.** The method claims to catch these; a one-in-ten miss rate on
its own core classes would make the claim unusable.

**F2 · Either baseline detects 90% or more of what the full package detects,
over the whole battery.** If the cheap baselines are within a tenth of the
apparatus, the apparatus is not worth its cost.

**F3 · Any one of the eight mechanisms produces zero additional escapes when
ablated.** A mechanism with no measured marginal contribution over this battery
should not be claimed as a component of the method; it should be dropped, or the
battery should be declared inadequate to test it.

**F4 · The negative control class is detected at more than 5%.** A method that
fires on comment edits is reporting noise, and every other rate in the study
would need to be discounted.

**F5 · Fewer than four of the twelve classes show a detection rate above 90%.**
A method whose per-class profile is uniformly mediocre is not a method, it is a
collection of partial heuristics.

Criteria deliberately NOT used:

- The aggregate detection rate over the whole battery. It is a function of how
  many instances each class contributes, which is a design choice of this study,
  not a property of the method.
- Any comparison against the existing twelve-mutant study in the subject
  package. That study was written by the same hand that wrote the checks, on
  cases chosen to illustrate them, and its purpose is demonstration rather than
  measurement.

---

## 4 · What is fixed and what is still open at commit time

**Fixed by this document:** the taxonomy, the operational definitions, the
enumeration rules, the seed, the three oracles, the ablation procedure, every
per-class prediction, and the five refutation criteria.

**Not fixed, and reported with the results:** the exact number of instances each
class yields, since that follows mechanically from the enumeration rules applied
to the subject package; the wall-clock cost; and whether any class had to be
sampled more aggressively than planned for the study to finish, which will be
declared if it happens.
