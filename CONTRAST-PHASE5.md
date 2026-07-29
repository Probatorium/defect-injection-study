# Contrast · Phase 5 against the preregistration committed in bfd1cbc

Subject A only, at `a3390860c53290271b6d06745fe252bfa7200dac`. Seed 20260728,
unchanged. The eight preregistered ablation configurations are untouched; one
was added. `PREREGISTRATION-PHASE5.md` has not been edited.

Battery **411**: the 365 of phase 3, unchanged class by class, plus 10
`silent_propagation` and 36 `unsupported_claim`.

## 1 · Class 14 · `silent_propagation`

**0 detected of 10. Escape rate 1.000.**

Predicted: escape at or above 0.80, most likely 1.000. **Held.**

All ten candidates passed the mechanical filter, so none was rejected: every one
is a real change to the computation that leaves every frozen claim rendering to
exactly the string it rendered before. What escapes is therefore not a list of
edits someone believed were silent. It is ten edits measured to be silent.

| Candidate | The change |
| --- | --- |
| `guard_digits_spigot` | 30 guard digits become 45 |
| `guard_digits_machin` | 20 guard places become 35 |
| `spigot_array_slack` | the remainder array gains two cells |
| `series_threshold_a` | the incomplete gamma series stops at 1e-13 instead of 1e-17 |
| `series_cap_a` | the iteration cap halves, 100000 to 50000 |
| `erfc_threshold_b` | the erf series stops at 1e-14 instead of 1e-18 |
| `erfc_cap_b` | the iteration cap halves, 10000 to 5000 |
| `machin_scale_slack` | five more fixed-point places |
| `equivalent_fraction` | `Fraction(1, 10)` built as `Fraction(2, 20)` |
| `equivalent_sqrt` | division by `sqrt(2)` becomes multiplication by `2 ** -0.5` |

**The named exception did not materialise, and that is a failed sub-prediction.**
`erfc_threshold_b` was singled out in advance because `check_30` pins the
hand-rolled `erfc_series` against the standard library over the range 0 to 3 at
a tolerance of 1e-12, and that pin is not a frozen claim. Loosening the series
threshold by four orders of magnitude was not enough to leave that tolerance.
It escaped with the other nine.

**This is the method's blind spot, now measured rather than declared.** Every
prior statement that Stasis cannot see a change that moves no published number
was an argument. It is now a rate: 0 of 10, on changes that a reader of the
diff would call substantive.

## 2 · Class 15 · `unsupported_claim`

**36 detected of 36. Rate 1.000.**

Caught by exactly one check, in all 36 cases: **`COV-orphan-numbers`**, which
lives in `checks/check_50_manuscript_coverage.py`.

### The two competing predictions

**Prediction A, the auditor's — REFUTED.** Ablating mechanism 2 produced **zero**
new escapes, the same as in phase 1 and phase 3. `check_90_claim_map.py`, which
is all that configuration removes, checks that the README's map mentions every
manuscript section and every check module. It never reads a number in the
manuscript.

**Prediction B, mine — CONFIRMED.** Ablating mechanism 1, which bundles
`check_50`, lets all 36 escape.

The added ninth configuration isolates the question:

| Configuration | New escapes | What it removes |
| --- | ---: | --- |
| 2 claim-to-check map | 0 | `check_90_claim_map.py` |
| 1 frozen claims | 157 | `check_40`, `check_50`, `check_60` |
| **2b manuscript number coverage alone** | **54** | `check_50` only |

The 54 decompose exactly: 36 `unsupported_claim`, plus the 18
`constant_copied_to_prose` that the orphan scan was already catching before
phase 1. The other 6 of that class are caught by the occurrence rule, which
lives in `check_40`. **`check_50` alone holds 13.1% of the battery.**

What this settles and what it does not: as the package stands today, the ability
to refuse an unsupported number lives in mechanism 1. Whether it *should* be
classified under the claim-to-check map is a design decision, and it is now a
decision to be made against a measurement instead of an argument.

## 3 · Measurement · the gate as position of failure

| Checks that ran, with the gate | without it | Mutants |
| ---: | ---: | ---: |
| 109 | 95 | 406 |
| 109 | not applicable | 1 |
| 14 | **0** | **4** |

**Predicted 14 against 95 for the four `data_truncated` mutants. Measured 14
against 0. The prediction FAILED.**

It failed in the direction that makes the mechanism more valuable, not less.
Removing the gate does not move the failure later in the run. It removes the
failure report altogether: without the structural invariants the truncated
sequence reaches `frozen_claims.render`, which raises when a non-integer is
formatted as an integer, and the verifier dies before any check reports
anything. With the gate, the run stops after 14 checks and names the invariant
that failed.

So mechanism 5's contribution, stated as a measurement rather than as a
detection count: **it converts an uncaught crash into a named structural failure
after a bounded number of checks.** Its zero in the ablation column was the
right answer to the wrong question, twice.

The row marked *not applicable* is one negative-control mutant that edits a
comment inside `check_10_structural_invariants.py`; the configuration that
ablates mechanism 5 deletes that file, so the defect cannot be injected. It is
excluded rather than counted as a crash, which would have overstated the
mechanism by one mutant. The first version of this report did count it, and said
five where the truth is four.

## 4 · The five declared surprises

| | Surprise | Materialised |
| --- | --- | :-: |
| **T1** | `silent_propagation` detected above 0.20 | **no** |
| **T2** | `unsupported_claim` not detected at 1.000 | **no** |
| **T3** | ablating mechanism 2 changing anything | **no** |
| **T4** | a gate-truncated run outside `data_truncated` | **no** |
| **T5** | any previously measured class moving | **no** |

None of the five. All thirteen classes carried over from phase 3 measured
identically, which is what T5 was watching for.

Two sub-predictions inside the document failed and are recorded as failed: the
named `erfc_series` exception in section 1, and the 95 in section 3.

## 5 · Totals

| | Phase 3 | Phase 5 |
| --- | ---: | ---: |
| Battery | 365 | 411 |
| Detected under oracle A | 327 · 0.896 | **363 · 0.883** |

The pooled rate fell while nothing got worse. It fell because the battery gained
46 mutants of which 10 are, by construction, undetectable. That is the arithmetic
of adding a class the method cannot see, and it is the reason the pooled rate has
never been used as a criterion in this study.
