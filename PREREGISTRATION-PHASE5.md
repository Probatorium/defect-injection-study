# Preregistration · Phase 5 · Two new classes and one unexploited measurement

Alexis García Hurtado · 2026

**Committed before the first mutant of either new class is generated and before
anything is run.** The three preregistrations that precede it, and every result
already published, are untouched.

Motivated by an external audit. Two of the three items were proposed by the
auditor; the third is a number that has been sitting in the data unused.

## 0 · Scope, and why it is subject A only

Subject A costs 0.73 s per verification, subject B 19.13 s. The full battery
under ten configurations is a few minutes on A and most of an afternoon on B.
Phase 5 runs on **subject A only**, and nothing here is claimed for subject B.
Where a result depends on an architecture — a `checks/` directory that can be
ablated file by file — that is a property of subject A and is said so.

Seed **20260728**, unchanged from every previous subject A run. Both new classes
are enumerated exhaustively and consume no randomness, so the sampled classes
draw exactly what they drew before and the rest of the battery is unchanged.

## 1 · Class 14 · `silent_propagation`

**Definition.** A real change to the computation that leaves **every published
value intact**: a guard, a convergence threshold, an iteration cap, or an
algebraically equivalent rewriting of an intermediate. The arithmetic genuinely
differs; nothing the manuscript prints moves.

**Enumeration.** A declared list of computation parameters and intermediates,
each with one declared perturbation, in the same style as the existing
`derivation_written_by_hand` site list. Every candidate then passes through a
**mechanical filter**: it is applied to a throwaway copy, the analysis is run,
and the candidate is kept only if every frozen claim still renders to exactly
the string it rendered before. A candidate that moves a published value is not
an instance of this class and is rejected with its reason reported.

The filter is what makes the class honest. Without it the class would be a list
of edits I believed were silent; with it, silence is measured.

**Prediction: escape at or above 0.80, and most likely 1.000.** By construction
every value comparison passes, both derivation paths still render identically to
each other, the figure is a function of counts that did not move, and the
manuscript was never touched. No new literal is introduced, so the
cited-versus-computed scan has nothing to see.

**The one named exception.** `check_30_double_derivation.py` pins the
hand-rolled `erfc_series` against the standard library over the argument range 0
to 3 at a tolerance of 1e-12. That pin is not a frozen claim, so a candidate
that loosens the series' convergence threshold could pass the filter and still
be caught there. If exactly that candidate is detected and no other, the
prediction is confirmed rather than refuted, and the mechanism that caught it is
named.

**Why this class matters.** If it escapes, the blind spot is **measured rather
than declared**. Every previous statement that Stasis cannot see a change that
moves no published number has been an argument. This turns it into a number.

## 2 · Class 15 · `unsupported_claim`

**Definition.** A sentence is appended to a manuscript section carrying a
numeric literal that **no frozen claim backs and no package constant equals**.
It is not a copied constant; it is an assertion with nothing behind it.

**Enumeration.** Exhaustive over the six non-exempt manuscript sections crossed
with a declared list of values chosen so that none is the text of any claim and
none is a package constant.

### Two competing predictions, both recorded before the data

The auditor's prediction and mine disagree, and the disagreement is written down
rather than resolved by argument.

**Prediction A, the auditor's.** The class is caught by mechanism 2, the
claim-to-check map, and by that mechanism only. Ablating mechanism 2 therefore
goes from zero new escapes — which is what phase 1 and phase 3 both measured —
to detecting the whole class.

**Prediction B, mine, from reading the code.** The check that will catch this
class is `COV-orphan-numbers`, which lives in
`checks/check_50_manuscript_coverage.py`. The preregistered taxonomy maps the
`COV` prefix to **mechanism 1**, and `taxonomy.ABLATION_MODULES` bundles
`check_50` into mechanism 1's ablation. `check_90_claim_map.py`, which is all
that mechanism 2's ablation removes, reads the README's map and never looks at a
number in the manuscript. So as this study is currently preregistered,
prediction A **cannot** come true: ablating mechanism 2 will change nothing, and
ablating mechanism 1 will let the whole class escape.

I expect prediction B. I may be wrong about what the auditor means by mechanism
2, in which case the measurement will say so.

**Nothing preregistered is edited to settle this.** `ABLATION_MODULES` keeps its
eight configurations exactly as they are, so every rate already published stays
comparable. What is **added** is a ninth configuration, which removes nothing
that any existing configuration removes on its own:

```
"2b manuscript number coverage alone"  ->  remove check_50_manuscript_coverage.py
```

Adding a configuration cannot change the result of any other configuration. It
isolates the check the two predictions disagree about, which is the only way to
test the reclassification instead of arguing it.

**Prediction for the new configuration:** ablating `check_50` alone lets the
whole of `unsupported_claim` escape, and also lets escape the six
`constant_copied_to_prose` mutants that the occurrence rule catches.

## 3 · Measurement · the gate, as position of failure rather than detection

Mechanism 5, the structural invariants, measured **zero new escapes** when
ablated, in phase 1 and again in phase 3. That is the correct answer to the
question "does anything stop being detected without it", and it is the wrong
question to ask of a gate. A gate does not add detections. It decides **where**
the run stops.

**What is measured.** For every mutant, the number of checks that actually run —
that appear in the verifier's output — under the unablated package and under the
package with mechanism 5 removed. The verifier already reports this; the study
has never recorded it. A column `checks_run` is added to the raw file for that
purpose, and it changes no existing column.

**Prediction.** For the overwhelming majority of the battery the two numbers are
equal, because most mutants never trip a structural invariant. For the mutants
that do, the number with the gate is **14** — the results of
`check_10_structural_invariants.py` and nothing further — against **95** without
it, since the suite then runs everything except the fourteen checks that were
removed. The mutants that trip it are predicted to be the four
`data_truncated` instances and no others; `data_corrupted` changes a digit
without breaking the structure of the sequence, so it should not trip anything.

**Why it matters.** It converts "the gate contributes nothing measurable" into a
number for what it does contribute: how much of the analysis a corrupt input is
prevented from reaching before it is stopped.

## 4 · What would surprise me

**T1** · `silent_propagation` detected above 0.20, other than by the named
`erfc_series` exception.

**T2** · `unsupported_claim` not detected at 1.000 under the unablated package.
Something with no claim behind it is exactly what the coverage check exists to
refuse; if it escapes, that check does not do what it says.

**T3** · Ablating mechanism 2 changing the result for `unsupported_claim` at
all. That would mean I have misread `check_90`, and prediction A would stand.

**T4** · Any mutant outside `data_truncated` showing a gate-truncated run.

**T5** · Any previously measured class moving. The battery for the thirteen
existing classes is unchanged and the seed is unchanged; a moved rate would mean
the two new classes perturbed something they should not touch.

## 5 · Fixed here, reported afterwards

**Fixed:** both class definitions, both enumeration rules, the mechanical filter
for class 14, the seed, the ninth ablation configuration and the fact that the
eight existing ones are untouched, both competing predictions for class 15, the
gate measurement and its prediction, and T1 to T5.

**Reported with the results:** how many candidates the class 14 filter rejected
and why, the instance count of each new class, the wall-clock cost, and the
hashes of two runs.

If a prediction fails it is reported as failed. This document is not edited
after the run.
