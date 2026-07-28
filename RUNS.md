# Runs

Every execution of this study, in order, with what changed and which output
hashes belong to it. Nothing here is deleted when a run is superseded: a hash
that appeared in a commit message once must stay resolvable, or the record
becomes worse than no record.

**Current** marks the run whose output files are the ones committed now.

Hashes are SHA-256 of the file as committed, LF line endings.

---

## Subject A · minimal-verified-paper @ e6e4250

### A-1 and A-2 · first measurement and its confirmation

Preregistration `cce21f3`. Study code as committed in `368cb56`. Two full runs,
590 s and 611 s wall clock, different process scheduling.

```
study_report.md   ee0b4c8f4b8e74a753e7bbbb7b2e4dd7767315f94910e9c70015f792b3fc55cb
raw_results.tsv   8dce80ad481596bc94d68f37970f256a3b8700dd8b59dc268cf7832a02a766d4
```

Both runs produced byte-identical files. Superseded by A-3 for the report only.

### A-3 and A-4 · after subject pinning · **CURRENT for subject A**

Study code as committed in `ebf2c78`. What changed: the subject path became
configurable and the study began refusing to run unless the subject is at the
declared commit with a clean worktree. The report gained
`SUBJECT_COMMIT_DECLARED`, `SUBJECT_COMMIT_FOUND`, `SUBJECT_WORKTREE` and
`SUBJECT_PINNED` in its header. **No measurement changed.** Two further full
runs, 576 s and 566 s.

```
study_report.md   fed635dacf1a65dbaf8ff8105c43c223ebb5d281247fffc625fc034c9eee25ed
raw_results.tsv   8dce80ad481596bc94d68f37970f256a3b8700dd8b59dc268cf7832a02a766d4
```

Note the raw hash: `8dce80ad…` is the same file A-1 produced. Four independent
runs across a change to the harness produced one identical body of measurements;
only the report header moved. That is the ambiguity this file exists to close —
two different report hashes, one unchanged set of results.

Verdicts, identical in A-1 through A-4: **F1 met, F3 met**, F2, F4 and F5 not
met.

---

## Subject B · kingwen-orderings-replication @ 73d9a77

### B-1 · first measurement · **CURRENT for subject B**

Preregistration `3c7da8a`, committed before the first mutant of subject B was
generated. Seed 20260729. 176 mutants, 885 jobs, 2874 s wall clock across 12
workers.

```
study_report_b.md   9e267256543e56c3f7baf2520b35bff680b37dd25f70196167eec24099c5dfc9
raw_results_b.tsv   c1e7496166331c44f9bf944f744f553afcb1d5eb134a8477cba25dd222be54c5
comparison.md       42a8fc1e91d80df940837ef796ea7fe4551deefb7b7d39f64aeb39a93a24f740
```

Verdict: **G1 breached for one class**, `manuscript_number_edited`, at −0.455.
G2, G3 and G4 not met.

**Cost note.** One verification of subject B takes 18.6 s on an idle machine and
roughly 35 to 40 s under twelve-way load, against subject A's 0.72 s. That is
why several of subject B's classes are sampled rather than enumerated
exhaustively, with sizes declared in `taxonomy_b.py`.

### Known defect in the B-1 instrument, disclosed rather than corrected

Two of the sixteen `derivation_written_by_hand` mutants **do not satisfy that
class's own operational definition**, which requires the hand-written literal to
equal the value the derivation currently produces:

- `derivation_written_by_hand#003` sets `LOWER_MASK = 7`. The real value is
  **56**. This is a wrong-value mutant, not a hand-written-derivation mutant.
- `derivation_written_by_hand#001` sets `SD_INV = 86.32`. The real value is
  **86.30179604156567**. The rounded check still passes, but the unrounded value
  propagates elsewhere.

Both were detected, and both detections are of an incorrect literal that the
generator asserted without verifying, not of the defect class as defined. The
consequence is stated in both directions and neither number is suppressed:

```
as measured, all 16 mutants          2/16 = 0.125
among the 14 that meet the definition 0/14 = 0.000
```

The preregistered prediction for this class was 0.00. It is recorded as
**failed at the measured rate of 0.125**, and the instrument defect is recorded
next to it. Rewriting the prediction, or quietly dropping the two invalid
mutants and reporting 0.000, would each be a way of making a failed prediction
look like a successful one.

Fixing the generator would change B-1's numbers and require a new run under a
new heading; it has not been done, and this entry is the reason a future B-2
would differ.

### B-2 · reproducibility confirmation

A second full run of B-1's code against the same pinned subject, to establish
that subject B's output is byte-identical across runs as subject A's is. Result
recorded here when it lands. Until then, **subject B's byte-for-byte
reproducibility is asserted by construction and not yet demonstrated**, which is
a weaker claim than the one made for subject A.

---

## What is not recorded here

Wall-clock timings appear in this file but never inside the result files
themselves, which carry no timestamp, no sandbox path and no duration, so that
two runs of the same code against the same subject produce identical bytes.
