"""The defect taxonomy, declared before any mutant is generated.

This file is the pre-registration of the experiment. Each class carries an
operational definition precise enough that a generator can enumerate its
instances mechanically, and a prediction written down before the study was run.
The predictions are here so that a surprising result stays visible as a surprise
rather than being reinterpreted afterwards.

Four of the twelve classes are expected to escape the method wholly or largely.
An experiment whose every class is caught measures nothing: it cannot
distinguish a method that works from an outcome that was arranged.

The subject of the study is the package at ../minimal-verified-paper. Nothing in
this directory modifies it. Every mutation is applied to a throwaway copy.
"""

from collections import namedtuple

DefectClass = namedtuple(
    "DefectClass",
    "key title definition enumeration prediction",
)

#: Seed for every sampling decision in this study. Declared here, used nowhere
#: else, and printed in the report.
SEED = 20260728

#: The subject package, relative to this directory.
SUBJECT = "../minimal-verified-paper"


CLASSES = (
    DefectClass(
        key="manuscript_number_edited",
        title="Number edited in the prose",
        definition=(
            "A numeric literal reported in paper.md is changed to a neighbouring "
            "value by incrementing its final digit, preserving the format. The "
            "computation is untouched, so the text and the code now disagree."
        ),
        enumeration=(
            "Exhaustive over the frozen claims: one mutant per claim whose text "
            "occurs in its declared manuscript section."
        ),
        prediction="Detected. This is the defect the method was built for.",
    ),
    DefectClass(
        key="constant_copied_to_prose",
        title="Constant copied into the prose by hand",
        definition=(
            "A sentence is appended to a manuscript section containing a numeric "
            "literal lifted from a package constant. The value is not wrong; it "
            "was simply typed into the text rather than derived, so nothing holds "
            "it to the code."
        ),
        enumeration=(
            "Exhaustive over the cross product of the six non-exempt manuscript "
            "sections and six package constants. Three of the six constants are "
            "also the text of some frozen claim and three are not; the design is "
            "balanced on purpose."
        ),
        prediction=(
            "Split. Detected when the copied value is not the text of any frozen "
            "claim. Escapes when it happens to coincide with one, because the "
            "coverage check matches by string and cannot know the role a number "
            "is playing in a sentence."
        ),
    ),
    DefectClass(
        key="derivation_written_by_hand",
        title="Derivation replaced by a hand-written value",
        definition=(
            "A function that computes a reported quantity is replaced by a return "
            "of the literal value it currently produces. The result is correct "
            "today and will not follow the data tomorrow."
        ),
        enumeration=(
            "Exhaustive over a declared list of derivation sites in the two "
            "statistics modules and the analysis orchestration."
        ),
        prediction=(
            "Split. Detected only by the cited-versus-computed check, and only "
            "when the value is distinctive enough to be guarded. A hand-written "
            "single-digit integer such as the degrees of freedom escapes by "
            "construction, because that check does not police integers below ten."
        ),
    ),
    DefectClass(
        key="figure_governing_number",
        title="Number that governs the drawing",
        definition=(
            "A module-level constant in the figure renderer is changed. No number "
            "in the manuscript moves; only the picture does."
        ),
        enumeration="Exhaustive over the module-level numeric constants of src/figure.py.",
        prediction="Detected by the byte comparison of the committed figure.",
    ),
    DefectClass(
        key="figure_gone_stale",
        title="Committed figure no longer matches the data",
        definition=(
            "A numeric text node inside the committed SVG is altered, as if the "
            "analysis had moved on and the image had not been regenerated."
        ),
        enumeration="Exhaustive over the numeric text nodes of the committed figure.",
        prediction="Detected by the byte comparison, and by any workflow that rebuilds figures.",
    ),
    DefectClass(
        key="frozen_value_edited",
        title="Frozen value edited in the claim table",
        definition=(
            "The frozen string of a claim in src/frozen_claims.py is changed to a "
            "neighbouring value. The manuscript is untouched."
        ),
        enumeration="Exhaustive over the frozen claims.",
        prediction="Detected. The mirror image of the first class.",
    ),
    DefectClass(
        key="result_embedded_in_code",
        title="Computed result embedded in the source",
        definition=(
            "A dead assignment carrying a currently-correct reported value is "
            "inserted into a source module. Nothing reads it; it is a copy waiting "
            "to drift."
        ),
        enumeration=(
            "Exhaustive over the cross product of a declared list of source "
            "modules and a declared list of reported values, half of them below "
            "the guarding threshold."
        ),
        prediction=(
            "Split. Detected for guarded values, escapes for small integers, by "
            "the stated design of that check."
        ),
    ),
    DefectClass(
        key="forbidden_phrase",
        title="Forbidden phrase reintroduced",
        definition=(
            "One phrase from the watch list is appended to one watched surface."
        ),
        enumeration=(
            "Exhaustive over the cross product of the watch list and the watched "
            "surfaces."
        ),
        prediction="Detected on every watched surface.",
    ),
    DefectClass(
        key="front_matter_drift",
        title="Front matter drifted on one surface",
        definition=(
            "The title, author or year is altered on exactly one of the three "
            "surfaces that must agree, by dropping an accent, dropping a subtitle "
            "or shifting a digit."
        ),
        enumeration="Exhaustive over field, surface and perturbation kind.",
        prediction="Detected by exact comparison.",
    ),
    DefectClass(
        key="data_corrupted",
        title="Input data corrupted",
        definition=(
            "One digit of one derivation path is changed to a different digit."
        ),
        enumeration=(
            "Sampled: positions drawn without replacement from the whole sequence "
            "using the declared seed, because exhaustive enumeration over every "
            "digit would multiply the battery by a thousand."
        ),
        prediction=(
            "Detected, by the comparison between the two paths, and additionally "
            "by the published anchor when the position falls inside the cited "
            "prefix."
        ),
    ),
    DefectClass(
        key="data_truncated",
        title="Input data truncated or extended",
        definition=(
            "A derivation path returns one element fewer or one more than declared."
        ),
        enumeration="Exhaustive over the two paths and the two directions.",
        prediction="Detected at the structural gate, before any statistic exists.",
    ),
    DefectClass(
        key="permutation_no_statistical_effect",
        title="Permutation with no statistical effect",
        definition=(
            "Two elements of one derivation path are swapped. Every count, every "
            "statistic and every p-value is unchanged; only the order differs."
        ),
        enumeration=(
            "Sampled: position pairs drawn using the declared seed, restricted to "
            "pairs whose two digits differ, so that the swap is a real change."
        ),
        prediction=(
            "Detected only by the comparison between the two derivation paths. "
            "Invisible to every statistic in the paper, and correctly so: the test "
            "reported here is a function of the counts alone."
        ),
    ),
    DefectClass(
        key="nonnumeric_text_change",
        title="Comment or non-numeric prose changed",
        definition=(
            "A word is altered in a source comment, or a non-numeric sentence is "
            "altered in the manuscript or the README. No number, no claim and no "
            "watched phrase is involved."
        ),
        enumeration=(
            "Exhaustive over the source modules that carry a comment, plus a "
            "declared list of prose lines."
        ),
        prediction=(
            "Not detected, by any oracle. This class is the negative control. If "
            "the method flagged it, the method would be reporting noise."
        ),
    ),
)

CLASSES_BY_KEY = {defect_class.key: defect_class for defect_class in CLASSES}

#: Which mechanism of the method each check id prefix belongs to. Used to build
#: the mechanism-against-class matrix. The numbering is the one used in the
#: subject package's README.
MECHANISM_OF_PREFIX = {
    "FRZ": "1 frozen claims",
    "COV": "1 frozen claims",
    "FIG": "1 frozen claims",
    "MAP": "2 claim-to-check map",
    "DUAL": "3 double derivation",
    "MUT": "4 mutation study",
    "INV": "5 structural invariants",
    "PHR": "6 forbidden phrases",
    "CIT": "7 cited vs computed",
    "SPLIT": "7 cited vs computed",
    "FM": "8 front matter",
    "META": "9 suite self-description",
}

MECHANISMS = (
    "1 frozen claims",
    "2 claim-to-check map",
    "3 double derivation",
    "4 mutation study",
    "5 structural invariants",
    "6 forbidden phrases",
    "7 cited vs computed",
    "8 front matter",
)

#: Ablating a mechanism means removing the check modules that implement it, so
#: that the suite discovers and runs everything else. The second derivation path
#: is NOT removed when mechanism 3 is ablated: what is ablated is the mechanism,
#: meaning the comparison, not the code it compares.
ABLATION_MODULES = {
    "1 frozen claims": ("check_40_frozen_numbers.py",
                        "check_50_manuscript_coverage.py",
                        "check_60_figure.py"),
    "2 claim-to-check map": ("check_90_claim_map.py",),
    "3 double derivation": ("check_30_double_derivation.py",),
    "4 mutation study": ("check_95_mutation_evidence.py",),
    "5 structural invariants": ("check_10_structural_invariants.py",),
    "6 forbidden phrases": ("check_70_forbidden_phrases.py",),
    "7 cited vs computed": ("check_20_cited_constants.py",
                            "check_55_computed_not_hardcoded.py"),
    "8 front matter": ("check_80_front_matter.py",),
}


def mechanism_of(check_id):
    """Map a check id such as 'FRZ-chi_square' to the mechanism it belongs to."""
    prefix = check_id.split("-", 1)[0]
    return MECHANISM_OF_PREFIX.get(prefix, "unattributed")
