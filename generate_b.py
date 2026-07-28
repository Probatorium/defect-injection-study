"""Rule-based, seeded generation of the defect battery for subject B.

Same mutant shape as `generate.py`: one line-anchored textual substitution,
`{id, cls, path, line, old, new}`. The rules differ because the subject does:
a LaTeX manuscript, a single verification script, a landing page, and a
manuscript-facing check that only asks whether a frozen string is present
somewhere in the file.
"""

import ast
import io
import os
import random
import re

import taxonomy_b

HERE = os.path.dirname(os.path.abspath(__file__))
SUBJECT = os.environ.get("STASIS_SUBJECT_B") or os.path.normpath(
    os.path.join(HERE, taxonomy_b.SUBJECT))

SCRIPT = "verify_paper.py"
TEX = "paper.tex"
README = "README.md"
LANDING = "index.html"


def read(rel):
    with io.open(os.path.join(SUBJECT, *rel.split("/")), encoding="utf-8") as fh:
        return fh.read()


def lines_of(rel):
    rows = read(rel).split("\n")
    if rows and rows[-1] == "":
        rows.pop()
    return rows


def bump(literal):
    """Increment the final digit of a literal, preserving its shape."""
    literal = str(literal)
    if not literal or not literal[-1].isdigit():
        return literal + "0"
    return literal[:-1] + str((int(literal[-1]) + 1) % 10)


class Battery(object):
    def __init__(self):
        self.mutants = []
        self._seen = set()
        self.rejected_duplicates = 0
        self.rejected_unanchored = 0

    def add(self, cls, path, line, old, new):
        rows = lines_of(path)
        if line is None or line < 1 or line > len(rows) or old not in rows[line - 1]:
            self.rejected_unanchored += 1
            return
        key = (path, line, old, new)
        if key in self._seen:
            self.rejected_duplicates += 1
            return
        self._seen.add(key)
        index = sum(1 for m in self.mutants if m["cls"] == cls)
        self.mutants.append(dict(id="%s#%03d" % (cls, index), cls=cls,
                                 path=path, line=line, old=old, new=new))


def _first_line_containing(rel, needle, skip=0):
    for number, row in enumerate(lines_of(rel), start=1):
        if needle in row:
            if skip:
                skip -= 1
                continue
            return number
    return None


# --------------------------------------------------------------------------
# The 29 strings subject B requires to appear verbatim in paper.tex.
# --------------------------------------------------------------------------
def frozen_strings():
    source = read(SCRIPT)
    block = re.search(r"frozen = \[(.*?)\]", source, re.S).group(1)
    return re.findall(r'"([^"]+)"', block)


def gen_manuscript_number_edited(battery):
    for value in frozen_strings():
        line = _first_line_containing(TEX, value)
        if line is not None:
            battery.add("manuscript_number_edited", TEX, line, value, bump(value))


# --------------------------------------------------------------------------
# A package constant retyped into the manuscript prose.
# --------------------------------------------------------------------------
#: Three are frozen strings the package guards; three are not. Balanced on
#: purpose, exactly as in subject A.
COPIED_CONSTANTS = ("1013", "1008", "2016", "424242", "20000", "4096")


def gen_constant_copied_to_prose(battery):
    anchors = [number for number, row in enumerate(lines_of(TEX), start=1)
               if row.startswith("\\section{")][:4]
    rows = lines_of(TEX)
    for anchor in anchors:
        for constant in COPIED_CONSTANTS:
            row = rows[anchor - 1]
            battery.add("constant_copied_to_prose", TEX, anchor, row,
                        row + "\n\nThe package carries the value " + constant
                        + " for this part of the work.")


# --------------------------------------------------------------------------
# A derivation replaced by the value it currently produces.
# --------------------------------------------------------------------------
#: Module-level constants whose right-hand side is a computation.
HAND_WRITTEN_CONSTANTS = (
    ("EXPECTED_INV = N * (N - 1) / 4", "EXPECTED_INV = 1008.0"),
    ("SD_INV = sqrt(N * (N - 1) * (2 * N + 5) / 72)", "SD_INV = 86.32"),
    ("MAX_INV = N * (N - 1) // 2", "MAX_INV = 2016"),
    ("LOWER_MASK = line_bit(1) | line_bit(2) | line_bit(3)", "LOWER_MASK = 7"),
)


def _check_call_sites():
    """Every check(...) whose reproduced and paper arguments are both usable.

    Returns [(line, reproduced_source, paper_literal_source)], found with ast so
    that comments and strings cannot be mistaken for code.
    """
    source = read(SCRIPT)
    rows = source.split("\n")
    tree = ast.parse(source)
    sites = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "check" and len(node.args) >= 4):
            continue
        reproduced, paper = node.args[2], node.args[3]
        if not isinstance(paper, ast.Constant) or isinstance(paper.value, (bool, str)):
            continue
        if isinstance(reproduced, ast.Constant):
            continue
        if reproduced.lineno != paper.lineno:
            continue
        line = paper.lineno
        row = rows[line - 1]
        paper_text = ast.get_source_segment(source, paper)
        reproduced_text = ast.get_source_segment(source, reproduced)
        if not paper_text or not reproduced_text or paper_text not in row:
            continue
        sites.append((line, reproduced_text, paper_text))
    return sites


def gen_derivation_written_by_hand(battery, rng, sample_size):
    for old, new in HAND_WRITTEN_CONSTANTS:
        line = _first_line_containing(SCRIPT, old)
        if line is not None:
            battery.add("derivation_written_by_hand", SCRIPT, line, old, new)
    sites = _check_call_sites()
    chosen = sorted(rng.sample(sites, min(sample_size, len(sites))))
    for line, reproduced_text, paper_text in chosen:
        # The computation is replaced by the number it currently yields, so the
        # check still passes and only a cited-versus-computed rule could object.
        battery.add("derivation_written_by_hand", SCRIPT, line,
                    reproduced_text + ", " + paper_text,
                    paper_text + ", " + paper_text)


# --------------------------------------------------------------------------
# The value the manuscript is supposed to print, edited in the check itself.
# --------------------------------------------------------------------------
def gen_frozen_value_edited(battery, rng, sample_size):
    sites = _check_call_sites()
    chosen = sorted(rng.sample(sites, min(sample_size, len(sites))))
    for line, _reproduced, paper_text in chosen:
        battery.add("frozen_value_edited", SCRIPT, line,
                    ", " + paper_text, ", " + bump(paper_text))


# --------------------------------------------------------------------------
# A reported result embedded in the source as a dead assignment.
# --------------------------------------------------------------------------
EMBEDDED_VALUES = ("1013", "1008", "2016", "86.3", "0.0034", "9")


def gen_result_embedded_in_code(battery):
    line = _first_line_containing(SCRIPT, "N = 64")
    rows = lines_of(SCRIPT)
    for value in EMBEDDED_VALUES:
        row = rows[line - 1]
        battery.add("result_embedded_in_code", SCRIPT, line, row,
                    row + "\n\n#: Copy of a reported result, kept next to the code.\n"
                    "CACHED_REPORTED_VALUE = " + value)


# --------------------------------------------------------------------------
# Forbidden phrases, split into what subject B watches and what it does not.
# --------------------------------------------------------------------------
EM_DASH = chr(0x2014)

#: Phrases subject A watches and subject B does not. The escape they are
#: expected to produce is the measured cost of a two-item watch list.
UNWATCHED_PHRASES = ("TODO", "FIXME", "we prove", "this proves", "highly significant",
                     "accept the null", "lorem ipsum", "citation needed")


def gen_forbidden_phrase(battery):
    # Watched: an em dash in the manuscript, and a pending-DOI announcement on
    # each living surface.
    rows = lines_of(TEX)
    battery.add("forbidden_phrase_watched", TEX, len(rows), rows[-1],
                rows[-1] + "\n% A closing remark " + EM_DASH + " with an em dash.")
    for surface in (README, LANDING):
        rows = lines_of(surface)
        battery.add("forbidden_phrase_watched", surface, len(rows), rows[-1],
                    rows[-1] + "\n\nA closing remark: DOI pending here.")
    # Unwatched: phrases subject B does not police.
    for surface in (README, LANDING):
        rows = lines_of(surface)
        for phrase in UNWATCHED_PHRASES:
            battery.add("forbidden_phrase_unwatched", surface, len(rows), rows[-1],
                        rows[-1] + "\n\nA closing remark: " + phrase + " here.")


# --------------------------------------------------------------------------
# Front matter drift.
# --------------------------------------------------------------------------
def _canonical_strings():
    tex = read(SCRIPT)
    values = {}
    for field, pattern in (("title", r'canonical title, read from paper\.tex",\s*\n\s*title, "(.+?)"\)'),
                           ("subtitle", r'canonical subtitle, read from paper\.tex",\s*\n\s*subtitle, "(.+?)"\)'),
                           ("author", r'canonical author, read from paper\.tex",\s*\n\s*author, "(.+?)"\)')):
        found = re.search(pattern, tex)
        if found:
            values[field] = found.group(1)
    doi_version = re.search(r'doi_version = "(.+?)"', tex)
    doi_concept = re.search(r'doi_concept = "(.+?)"', tex)
    if doi_version:
        values["doi_version"] = doi_version.group(1)
    if doi_concept:
        values["doi_concept"] = doi_concept.group(1)
    return values


#: One perturbation per field, chosen so that it is a realistic slip rather than
#: a mangling: a hyphen where a space belongs, a dropped surname, a shifted digit.
PERTURBATIONS = {
    "title": ("I Ching", "I-Ching"),
    "subtitle": ("Limits", "Limit"),
    "author": (" Hurtado", ""),
    "doi_version": None,
    "doi_concept": None,
}


def gen_front_matter_drift(battery):
    values = _canonical_strings()
    for field, value in sorted(values.items()):
        perturbation = PERTURBATIONS.get(field)
        for surface in (TEX, README, LANDING):
            for number, row in enumerate(lines_of(surface), start=1):
                if value not in row:
                    continue
                if perturbation is None:
                    battery.add("front_matter_drift", surface, number,
                                value, bump(value))
                elif perturbation[0] in row:
                    battery.add("front_matter_drift", surface, number,
                                perturbation[0], perturbation[1])


# --------------------------------------------------------------------------
# The input data: the embedded King Wen table.
# --------------------------------------------------------------------------
def _king_wen_close_line():
    rows = lines_of(SCRIPT)
    start = None
    for number, row in enumerate(rows, start=1):
        if row.startswith("KING_WEN = ["):
            start = number
        elif start and row.strip() == "]":
            return number
    return None


def gen_data_corrupted(battery, rng, sample_size):
    close = _king_wen_close_line()
    rows = lines_of(SCRIPT)
    positions = sorted(rng.sample(range(64), sample_size))
    for position in positions:
        row = rows[close - 1]
        battery.add("data_corrupted", SCRIPT, close, row,
                    row + "\nKING_WEN[%d] = (KING_WEN[%d] + 1) %% 64"
                    % (position, position))


def gen_data_truncated(battery):
    close = _king_wen_close_line()
    rows = lines_of(SCRIPT)
    row = rows[close - 1]
    battery.add("data_truncated", SCRIPT, close, row, row + "\nKING_WEN = KING_WEN[:-1]")
    battery.add("data_truncated", SCRIPT, close, row, row + "\nKING_WEN = KING_WEN + [0]")


# --------------------------------------------------------------------------
# The negative control.
# --------------------------------------------------------------------------
PROSE_CONTROL = (
    (README, "A verification package is worth what it catches.",
     "A verification package is worth exactly what it catches."),
    (README, "Every claim in the paper maps to a named check",
     "Every claim in the paper maps to one named check"),
)


def gen_nonnumeric_text_change(battery, limit=10):
    added = 0
    for number, row in enumerate(lines_of(SCRIPT), start=1):
        stripped = row.strip()
        if stripped.startswith("#") and not stripped.startswith("#!") \
                and len(stripped) > 40 and added < limit:
            battery.add("nonnumeric_text_change", SCRIPT, number, row, row + " Reviewed.")
            added += 1
    for surface, old, new in PROSE_CONTROL:
        line = _first_line_containing(surface, old)
        if line is not None:
            battery.add("nonnumeric_text_change", surface, line, old, new)


def build():
    rng = random.Random(taxonomy_b.SEED)
    battery = Battery()
    gen_manuscript_number_edited(battery)
    gen_constant_copied_to_prose(battery)
    gen_derivation_written_by_hand(battery, rng, taxonomy_b.SAMPLE_DERIVATION_CHECK_SITES)
    gen_frozen_value_edited(battery, rng, taxonomy_b.SAMPLE_FROZEN_VALUE_EDITED)
    gen_result_embedded_in_code(battery)
    gen_forbidden_phrase(battery)
    gen_front_matter_drift(battery)
    gen_data_corrupted(battery, rng, taxonomy_b.SAMPLE_DATA_CORRUPTED)
    gen_data_truncated(battery)
    gen_nonnumeric_text_change(battery)
    return battery


if __name__ == "__main__":
    b = build()
    counts = {}
    for mutant in b.mutants:
        counts[mutant["cls"]] = counts.get(mutant["cls"], 0) + 1
    for cls in sorted(counts):
        print("%-38s %4d" % (cls, counts[cls]))
    print("%-38s %4d" % ("TOTAL", len(b.mutants)))
    print("rejected duplicates: %d, unanchored: %d"
          % (b.rejected_duplicates, b.rejected_unanchored))
