# Subject A against subject B, class by class

Subject A's counts are read back from `results/raw_results.tsv`, not
copied by hand. Differences are B minus A, with Newcombe's hybrid score
interval at 95%, which is built from the two Wilson intervals and stays
sensible when a rate sits at 0 or 1, as several do here.

`G1` is the preregistered criterion: for a class both subjects implement,
a difference larger than 0.25 refutes the claim that its detection rate is
a property of the method. `G0` excludes from G1 the classes where subject B
has no corresponding mechanism at all.

| Class | n A | rate A | n B | rate B | diff (B−A) | 95% Newcombe | in G1 | verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- | :-: | --- |
| `constant_copied_to_prose` | 36 | 0.500 | 24 | 0.000 | -0.500 | -0.655 to -0.292 | no | G0: mechanism absent in B |
| `data_corrupted` | 30 | 1.000 | 20 | 1.000 | +0.000 | -0.161 to 0.114 | yes | within margin |
| `data_truncated` | 4 | 1.000 | 2 | 1.000 | +0.000 | -0.658 to 0.490 | yes | within margin |
| `derivation_written_by_hand` | 10 | 0.700 | 16 | 0.125 | -0.575 | -0.787 to -0.191 | no | G0: mechanism absent in B |
| `forbidden_phrase_unwatched` | — | — | 16 | 0.000 | — | — | no | no counterpart in subject A |
| `forbidden_phrase_watched` | 95 | 1.000 | 3 | 1.000 | +0.000 | -0.561 to 0.039 | yes | within margin |
| `front_matter_drift` | 20 | 0.550 | 23 | 0.522 | -0.028 | -0.300 to 0.251 | yes | within margin |
| `frozen_value_edited` | 31 | 1.000 | 25 | 0.800 | -0.200 | -0.391 to -0.043 | yes | within margin |
| `manuscript_number_edited` | 31 | 0.903 | 29 | 0.448 | -0.455 | -0.631 to -0.222 | yes | **G1 BREACHED** |
| `nonnumeric_text_change` | 19 | 0.000 | 12 | 0.000 | +0.000 | -0.168 to 0.242 | yes | within margin |
| `result_embedded_in_code` | 32 | 0.938 | 6 | 0.000 | -0.938 | -0.983 to -0.523 | no | G0: mechanism absent in B |
| `figure_gone_stale` | 27 | 1.000 | — | — | — | — | no | not applicable to B: subject B commits no regenerable image; the only picture in the repository is a logo that no computation produces |
| `figure_governing_number` | 8 | 1.000 | — | — | — | — | no | not applicable to B: subject B has no figure renderer; there is no constant that governs a drawing because there is no drawing |
| `permutation_no_statistical_effect` | 20 | 1.000 | — | — | — | — | no | not applicable to B: subject B's object of study IS an ordering, and every reported statistic is a function of that order, so no permutation of the input is statistically inert |

## Preregistered criteria

- **G1** per class, margin 0.25: **BREACHED for 1 class(es)** — manuscript_number_edited (-0.455)
- **G2** more than half of the 7 jointly-implemented classes breach G1: **not met** (1 of 7)
- **G3** negative control differs by more than 0.05: **not met** — A 0.000, B 0.000
- **G4** same rate reached by different mechanisms: see the mechanism
  attribution in each subject's own report; mechanism 3 is not measured
  for subject B and no generalisation about it is supported.

