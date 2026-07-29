"""Subject B: what applies, what is excluded, how each mechanism is ablated.

The companion to `taxonomy.py`, which governs subject A and is not touched.
Every decision here is the one written down in `PREREGISTRATION-SUBJECT-B.md`
before the first mutant of subject B was generated; this file is that document
in executable form, not a revision of it.
"""

#: Seed for every sampling decision on subject B. Declared, and printed in the
#: report. Different from subject A's on purpose: reusing a seed across subjects
#: would create a coincidence nobody could interpret.
SEED = 20260729

#: Default location of the subject, relative to this directory: a sibling clone.
SUBJECT = "../kingwen-orderings-replication"

#: The commit subject B's numbers belong to. The study refuses to run against
#: any other unless explicitly forced.
DECLARED_COMMIT = "73d9a77cdc59ea1410ae815cbb484dc68eb752d1"

#: Classes of `taxonomy.CLASSES` that do NOT apply to subject B, with the
#: structural reason. Reproduced from the preregistration so that the exclusion
#: travels with the code.
EXCLUDED_CLASSES = {
    "figure_governing_number":
        "subject B has no figure renderer; there is no constant that governs a "
        "drawing because there is no drawing",
    "figure_gone_stale":
        "subject B commits no regenerable image; the only picture in the "
        "repository is a logo that no computation produces",
    "permutation_no_statistical_effect":
        "subject B's object of study IS an ordering, and every reported "
        "statistic is a function of that order, so no permutation of the input "
        "is statistically inert",
}

#: Ablation for subject B is textual: there is no checks/ directory to delete
#: from, so a mechanism is removed by neutralising its call in main() or the
#: individual check lines that implement it. Each entry is a list of
#: (path, old, new) replacements, each of which must match exactly once.
ABLATION_EDITS = {
    "1 frozen claims (manuscript half only)": [
        ("verify_paper.py", "    section_paper()", "    pass"),
    ],
    "5 structural invariants": [
        ("verify_paper.py", "    section_0()", "    pass"),
    ],
    "6 forbidden phrases": [
        ("verify_paper.py",
         '    check("tex", "paper.tex contains no em dash", tex.count(chr(0x2014)), 0)',
         "    pass"),
        ("verify_paper.py",
         '        check("front", f"{name} no longer announces a pending DOI",\n'
         '              "DOI pending" not in surface, True)',
         "        pass"),
    ],
    "8 front matter": [
        ("verify_paper.py", "    section_front_matter()", "    pass"),
        ("verify_paper.py", "    section_pdf_metadata()", "    pass"),
    ],
}

MECHANISMS = tuple(ABLATION_EDITS)

#: Mechanisms that exist in subject A but cannot be ablated in subject B, with
#: the reason. Their rows read "not measured" in the comparison rather than zero,
#: because a zero would claim something that was never tested.
NOT_ABLATABLE = {
    "2 claim-to-check map":
        "the map exists in README.md but no check enforces it",
    "3 double derivation":
        "the independent re-derivation lives in a sibling repository that is "
        "not part of the subject and is not pinned; there is no check whose "
        "removal would constitute ablating it",
    "4 mutation study":
        "mutations are documented in the README as shell one-liners and "
        "enforced by no check",
    "7 cited vs computed":
        "the mechanism is absent from subject B",
}

#: Mechanism 1 is ablated only in its manuscript-facing half, so its ablation
#: number is not comparable with subject A's. Flagged here so the report can say
#: so instead of placing the two side by side.
NOT_COMPARABLE_ABLATION = ("1 frozen claims (manuscript half only)",)

#: Classes where subject B does not implement the mechanism that catches them in
#: subject A. Criterion G0 excludes these from the per-class generalisation test:
#: a large difference here measures what the two packages implement, which is
#: already known, not whether a rate generalises.
NOT_JOINTLY_IMPLEMENTED = (
    "constant_copied_to_prose",
    "derivation_written_by_hand",
    "result_embedded_in_code",
    "forbidden_phrase_unwatched",
)

#: Declared margin for criterion G1, in absolute difference of detection rate.
#: Wide on purpose: class sizes here are of the order of 20, so a 95% Wilson
#: interval is about 0.20 across and a tighter margin would fire on noise.
G1_MARGIN = 0.25

#: Declared margin for the negative control, criterion G3.
G3_MARGIN = 0.05

#: Sample sizes for the classes that are not enumerated exhaustively. Driven by
#: cost: one verification of subject B takes 18.6 s against subject A's 0.72 s.
SAMPLE_FROZEN_VALUE_EDITED = 25
SAMPLE_DERIVATION_CHECK_SITES = 12
SAMPLE_DATA_CORRUPTED = 20
