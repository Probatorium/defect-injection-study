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
that subject B's output is byte-identical across runs as subject A's is.

A first attempt was started and then **deliberately stopped**, because the two
columns added in R-1 below landed while it was running: it held the older code
in memory and would have overwritten the regenerated file with the previous
format on completion. It was run again against the published code, so that what
it confirms is what is published.

**Result: all three output files byte-identical.** 3475 s wall clock against
B-1's 2874 s, different process scheduling, same bytes.

```
study_report_b.md   9e267256543e56c3f7baf2520b35bff680b37dd25f70196167eec24099c5dfc9
raw_results_b.tsv   553fa55e2578423294ddd735da7aaebe2755bc3ef54ccc018619e13742aa47cf
comparison.md       42a8fc1e91d80df940837ef796ea7fe4551deefb7b7d39f64aeb39a93a24f740
```

Subject B's byte-for-byte reproducibility is now **demonstrated rather than
asserted**, which is the claim subject A already carried.

**A second thing this run establishes, which was not what it was for.** B-2 was
a full re-execution: it regenerated `raw_results_b.tsv` from scratch, including
the two columns R-1 had added by rewriting. Its output matches the rewritten
file exactly. So the rewrite did not merely preserve the columns it promised to
preserve — the file it produced is the same file a fresh run produces, which is
the stronger statement and the one that matters if anyone ever wonders whether a
regenerated file and a measured one can be trusted equally here.

---

## Rewrites of published files

### R-1 · two columns added to both raw files · **CURRENT**

`target_string` and `manuscript_occurrences` were added to
`raw_results.tsv` and `raw_results_b.tsv`, by `regenerate_raw.py`.

**No measurement changed, and none could have.** Nothing was re-run. The oracle
verdicts were read back out of the published files, each battery was rebuilt
from its declared seed, and the rows were written again through each study's own
`write_raw`, so the result is byte-identical to what the next full run of that
study will produce. Both new values are derived from the mutant and the subject,
neither of which moved. `regenerate_raw.py` refuses to write unless every column
that existed before still holds exactly the value it held before, and that check
passed for all 363 rows of subject A and all 176 of subject B; the preserved
columns were also diffed independently afterwards.

Why the columns exist: the published files let a reader check every rate, but
not re-derive the cross-tabulation that explains subject B's G1 breach. That
analysis used how often each target string occurs in the manuscript, and that
number was not in the file. It is now, and the cross-tabulation is one line of
`awk` away.

```
                              before R-1                                                        after R-1
raw_results.tsv     8dce80ad481596bc94d68f37970f256a3b8700dd8b59dc268cf7832a02a766d4   a30204f07570681811653881beb683dcff743793554fa10e3a121b90b1cfbfaf
raw_results_b.tsv   c1e7496166331c44f9bf944f744f553afcb1d5eb134a8477cba25dd222be54c5   553fa55e2578423294ddd735da7aaebe2755bc3ef54ccc018619e13742aa47cf
```

The three report files are untouched by R-1 and keep their hashes:
`fed635da…` for subject A, `9e267256…` for subject B, `42a8fc1e…` for the
comparison.

A defect in the rewriting tool, found and fixed before anything was published:
its first parser stripped the whole file before splitting, which ate the final
tab of the last row whenever that row's `killed_ids` was empty. Subject B's last
mutant escaped everything, so its `killed_ids` is empty and the parse failed
there. Both files were restored from backups and regenerated after the fix.

---

## Re-measurement of both subjects, after their repairs

Nothing above is corrected, replaced or removed. Those numbers are the record of
what the earlier apparatus caught, and a before-and-after table needs its before
to stay where it is.

### A-5 and A-6 · subject A at a339086 · **CURRENT for subject A**

Seed 20260728, unchanged. Ablations unchanged. `DECLARED_COMMIT` moved in
`37de4bf`, with its reason. Two full runs, 606 s and 607 s, byte-identical.

```
study_report.md   1a3b77fcfd27763c758ac5ffc92d2eacbca2562b5d0e94ac0be95e0ca180e33c
raw_results.tsv   7b644b3899dd99c95400d5c2e1396cb1c2c931806ea6c0a767fdb814b0d6dbaa
```

327 of 365 detected, against 309 of 363 before. The battery grew by two, both
for reasons recorded in `CONTRAST-REMEASUREMENT.md` section 6 and both reported
before the run.

### B-3 and B-4 · subject B at 95437d3 · **CURRENT for subject B**

Seed 20260729, unchanged. Ablations unchanged, and deliberately not extended to
the checks the repair added. `DECLARED_COMMIT` moved in `f7fc850`. The generator
was repaired first in `c83102c` and produces a battery identical to the
published one, class by class. Two full runs, 3219 s and 3482 s, byte-identical.

```
study_report_b.md   e47cfd5f4df07dff1cf424aa55827fc32a5654e7e723072f372be76007ff4837
raw_results_b.tsv   aef2dac90e444f4618cc0e70571ae49f43d924ae05d4ccb0f26a4e37f6acfb3d
comparison.md       d431bb489000294262400315a97dd5bd2f1403d428b131ffc44165f7bb3b0cad
```

123 of 176 detected, against 72 of 176 before.

### A-7 and A-8 · phase 5, two new classes and the gate measurement · **CURRENT for subject A**

Subject A at a339086, unchanged. Seed 20260728, unchanged. The eight
preregistered ablation configurations untouched; a ninth added in `phase5.py`,
outside `taxonomy.py`, for the same reason subject pinning went into
`subject.py`. Preregistration `bfd1cbc`. Two full runs, 777 s and 761 s,
byte-identical.

```
study_report.md   338c5c7068073e6615c12e0c94d231629a8ca817af7675b1098c66a620de7e27
raw_results.tsv   cdd9d9691b3ce33074df4ab050e4fb824e2435e59fa66efac2d3df1a08fa9d2f
```

Battery 411: the 365 of phase 3, identical class by class, plus 10
`silent_propagation` and 36 `unsupported_claim`. 363 of 411 detected. The raw
file gains a `checks_run` column, inserted before `killed_ids`, so columns 1 to
10 keep their positions and `killed_ids` moves from 11 to 12.

Two aggregation defects were found and fixed before anything was published, and
both are recorded because both produced a wrong statement in a generated report:

- the results dictionary is keyed by (kind, mutant id, configuration) and the
  first version of the gate measurement indexed it with a two-element key. The
  battery ran to completion, 4532 jobs in 831 s, and the run then died in
  aggregation. No measurement was affected; the compute was lost.
- the first corrected version counted five mutants as crashing without the gate.
  Four crash. The fifth is a negative-control mutant that edits a comment inside
  `check_10_structural_invariants.py`, and the configuration that ablates
  mechanism 5 deletes that file, so the defect cannot be injected at all. Such
  pairs are not applicable, not crashes, and counting it overstated the
  mechanism by one mutant.

`raw_results.tsv` carries the same hash across all four phase 5 runs, before and
after both fixes. Only the report moved.

### Which hash belongs to which apparatus

Two files carry the same name at four different hashes across this record. The
table exists so that a hash quoted in any commit message stays resolvable.

| File | Apparatus | Hash |
| --- | --- | --- |
| `raw_results.tsv` | A before, pre-columns | `8dce80ad4815…` |
| `raw_results.tsv` | A before, with columns | `a30204f07570…` |
| `raw_results.tsv` | A after, phase 3 | `7b644b3899dd…` |
| `raw_results.tsv` | **A after, phase 5** | `cdd9d9691b3c…` |
| `study_report.md` | A before, pre-pinning | `ee0b4c8f4b8e…` |
| `study_report.md` | A before, pinned | `fed635dacf1a…` |
| `study_report.md` | A after, phase 3 | `1a3b77fcfd27…` |
| `study_report.md` | **A after, phase 5** | `338c5c706807…` |
| `raw_results_b.tsv` | B before, pre-columns | `c1e749616633…` |
| `raw_results_b.tsv` | B before, with columns | `553fa55e2578…` |
| `raw_results_b.tsv` | **B after** | `aef2dac90e44…` |
| `study_report_b.md` | B before | `9e2672565435…` |
| `study_report_b.md` | **B after** | `e47cfd5f4df0…` |
| `comparison.md` | before | `42a8fc1e91d8…` |
| `comparison.md` | **after** | `d431bb489000…` |

The "before" files are kept in `results_before/` so that both halves of the
table can be re-derived without checking out an earlier commit.

## What is not recorded here

Wall-clock timings appear in this file but never inside the result files
themselves, which carry no timestamp, no sandbox path and no duration, so that
two runs of the same code against the same subject produce identical bytes.
