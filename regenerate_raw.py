#!/usr/bin/env python3
"""Rewrite both raw result files with the two added columns, without re-running.

    python regenerate_raw.py

The measurements are not recomputed and cannot change: this reads the oracle
verdicts back out of the existing files, rebuilds each battery from its declared
seed, and writes the same rows again with `target_string` and
`manuscript_occurrences` filled in. Both new columns are derived from the
mutant and the subject, neither of which has moved.

It writes through each study's own `write_raw`, so the regenerated files are
byte-identical to what the next full run of that study would produce. Anything
else would leave two file formats in circulation.

The script verifies, and refuses to write unless, every column that existed
before still holds exactly the value it held before.
"""

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import run_study                                                   # noqa: E402
import run_study_b                                                 # noqa: E402
import generate                                                    # noqa: E402
import generate_b                                                  # noqa: E402

RESULTS = os.path.join(HERE, "results")

#: Columns that existed before this change, and must survive it untouched.
PRESERVED = ("mutant_id", "class", "path", "line", "oracle_a", "oracle_b",
             "oracle_c", "checks_killed", "killed_ids")


def read_tsv(name):
    """Parse a results file without losing empty trailing fields.

    Stripping the whole text before splitting would eat the final tab of the
    last row whenever its `killed_ids` is empty, leaving that row one column
    short. The last mutant in subject B's file is one that escaped everything,
    so its `killed_ids` is empty and this went wrong on the first attempt.
    Rows are padded to the header width for the same reason.
    """
    path = os.path.join(RESULTS, name)
    rows = io.open(path, encoding="utf-8").read().split("\n")
    while rows and rows[-1] == "":
        rows.pop()
    header = rows[0].split("\t")
    records = []
    for row in rows[1:]:
        fields = row.split("\t")
        fields += [""] * (len(header) - len(fields))
        records.append(dict(zip(header, fields)))
    return header, records


def rebuild(name, battery, dead_separator):
    """Reconstruct the row objects `write_raw` expects from the published file."""
    _header, records = read_tsv(name)
    mutants = {mutant["id"]: mutant for mutant in battery.mutants}
    rows = []
    for record in records:
        identifier = record["mutant_id"]
        if identifier not in mutants:
            raise RuntimeError(
                "%s contains mutant %s which the current battery does not "
                "generate; the battery or the seed has changed and this file "
                "cannot be regenerated without re-running the study"
                % (name, identifier))
        dead = [d for d in record["killed_ids"].split(dead_separator) if d]
        rows.append(dict(mutant=mutants[identifier],
                         a=record["oracle_a"] == "1",
                         b=record["oracle_b"] == "1",
                         c=record["oracle_c"] == "1",
                         dead=dead))
    return records, rows


def verify_preserved(name, before):
    """Refuse to accept the rewrite unless every prior column is unchanged."""
    _header, after = read_tsv(name)
    if len(before) != len(after):
        raise RuntimeError("%s changed length: %d rows became %d"
                           % (name, len(before), len(after)))
    for old, new in zip(before, after):
        for column in PRESERVED:
            if old[column] != new[column]:
                raise RuntimeError(
                    "%s: mutant %s column %s changed from %r to %r; the rewrite "
                    "was supposed to add information, not alter it"
                    % (name, old["mutant_id"], column, old[column], new[column]))
    return len(after)


def main():
    print("subject A")
    before_a, rows_a = rebuild("raw_results.tsv", generate.build(), ",")
    run_study.write_raw(rows_a)
    print("  rewrote raw_results.tsv, %d rows, prior columns unchanged"
          % verify_preserved("raw_results.tsv", before_a))

    print("subject B")
    before_b, rows_b = rebuild("raw_results_b.tsv", generate_b.build(), " ~ ")
    run_study_b.write_raw(rows_b)
    print("  rewrote raw_results_b.tsv, %d rows, prior columns unchanged"
          % verify_preserved("raw_results_b.tsv", before_b))
    return 0


if __name__ == "__main__":
    sys.exit(main())
