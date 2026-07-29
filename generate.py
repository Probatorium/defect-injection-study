"""Rule-based, seeded generation of the defect battery.

Nothing here is chosen by hand. Every mutant is produced by applying a class's
enumeration rule to the subject package as it stands, so re-running this file on
the same subject yields the same battery in the same order.

A mutant is a single textual substitution anchored to one line:

    {id, cls, path, line, old, new}

Anchoring to a line rather than to a unique string matters: the manuscript
contains the literal "93" twice, and a whole-file substitution could not tell
the two apart. `new` may contain newlines, which is how insertions and
multi-line replacements are expressed.
"""

import io
import os
import random
import re
import sys

import phase5
import subject as subject_module
import taxonomy

HERE = os.path.dirname(os.path.abspath(__file__))
SUBJECT = subject_module.resolve()
sys.path.insert(0, SUBJECT)

from src import forbidden_phrases as fp          # noqa: E402
from src import frozen_claims as fc              # noqa: E402
from src import front_matter as fm               # noqa: E402


def read(rel):
    with io.open(os.path.join(SUBJECT, *rel.split("/")), encoding="utf-8") as fh:
        return fh.read()


def lines_of(rel):
    text = read(rel)
    out = text.split("\n")
    if out and out[-1] == "":
        out.pop()
    return out


def bump(literal):
    """Increment the final digit of a numeric literal, preserving its shape."""
    return literal[:-1] + str((int(literal[-1]) + 1) % 10)


def token_on_line(line, literal):
    """True if `literal` appears on `line` as a standalone numeric token."""
    return re.search(r"(?<![\w.])" + re.escape(literal) + r"(?![\w]|\.\d)", line) is not None


def section_line_range(rel, heading):
    """(first, last) 1-based line numbers of a '## heading' body, end exclusive."""
    rows = lines_of(rel)
    start = None
    for index, row in enumerate(rows, start=1):
        if row.startswith("## "):
            if start is not None:
                return start, index
            if row[3:].strip() == heading:
                start = index + 1
    return (start, len(rows) + 1) if start else (None, None)


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
        self.mutants.append(dict(id="%s#%03d" % (cls, sum(
            1 for m in self.mutants if m["cls"] == cls)),
            cls=cls, path=path, line=line, old=old, new=new))


# --------------------------------------------------------------------------
# Class 1: a number reported in the prose is edited.
# --------------------------------------------------------------------------
def gen_manuscript_number_edited(battery):
    rows = lines_of("paper.md")
    for claim in fc.CLAIMS:
        first, last = section_line_range("paper.md", claim.section)
        if first is None:
            continue
        target = None
        count_match = re.match(r"^count_(\d)$", claim.id)
        for number in range(first, last):
            row = rows[number - 1]
            if not token_on_line(row, claim.text):
                continue
            if count_match:
                # Target the table row for this specific digit, so that the two
                # digits sharing the count 93 give two distinct mutants.
                if row.strip().startswith("| `%s`" % count_match.group(1)):
                    target = number
                    break
            else:
                # Non-count claims are anchored in prose, never in a table row,
                # so that `largest_count` does not collide with `count_1`.
                if not row.strip().startswith("|"):
                    target = number
                    break
        if target is not None:
            battery.add("manuscript_number_edited", "paper.md", target,
                        claim.text, bump(claim.text))


# --------------------------------------------------------------------------
# Class 2: a package constant is retyped into the prose.
# --------------------------------------------------------------------------
#: Three of these are also the text of a frozen claim and three are not. The
#: split is the point of the class.
COPIED_CONSTANTS = ("1000", "100", "0.05", "30", "130", "239")

MANUSCRIPT_SECTIONS = ("1. Question", "2. Data", "3. Null model and test",
                       "4. Result", "5. What this does not show",
                       "6. How this paper verifies itself")


def gen_constant_copied_to_prose(battery):
    rows = lines_of("paper.md")
    for heading in MANUSCRIPT_SECTIONS:
        first, last = section_line_range("paper.md", heading)
        anchor = None
        for number in range(last - 1, first - 1, -1):
            if rows[number - 1].strip():
                anchor = number
                break
        for constant in COPIED_CONSTANTS:
            row = rows[anchor - 1]
            battery.add("constant_copied_to_prose", "paper.md", anchor, row,
                        row + "\n\nThe package carries the value " + constant
                        + " for this part of the work.")


# --------------------------------------------------------------------------
# Class 3: a derivation is replaced by the value it currently produces.
# --------------------------------------------------------------------------
HAND_WRITTEN_DERIVATIONS = (
    ("src/stats_path_a_series.py",
     "    return sum((observed - expected) ** 2 / expected for observed in counts)",
     "    return 4.74"),
    ("src/stats_path_b_exact.py",
     "    return Fraction(N_CATEGORIES * sum_of_squares, n) - n",
     "    return Fraction(237, 50)"),
    ("src/stats_path_a_series.py", "    return 1.0 - lower",
     "    return 0.8563586575252495"),
    ("src/stats_path_b_exact.py", "    return tail",
     "    return 0.8563586575252493"),
    ("src/stats_path_a_series.py", "    return (observed - expected) / sd",
     "    return 1.6865480854231356"),
    ("src/stats_path_a_series.py", "    return min(1.0, p * n_tests)",
     "    return 0.916902815494292"),
    ("src/frozen_claims.py", "    degrees_of_freedom = N_CATEGORIES - 1",
     "    degrees_of_freedom = 9"),
    ("src/frozen_claims.py", "    expected = Fraction(n, N_CATEGORIES)",
     "    expected = Fraction(100, 1)"),
    ("src/stats_path_a_series.py", "    return counts",
     "    return [93, 116, 103, 102, 93, 97, 94, 95, 101, 106]"),
    ("src/stats_path_b_exact.py",
     '    return [text.count(str(d)) for d in range(N_CATEGORIES)]',
     "    return [93, 116, 103, 102, 93, 97, 94, 95, 101, 106]"),
)


def gen_derivation_written_by_hand(battery):
    for path, old, new in HAND_WRITTEN_DERIVATIONS:
        rows = lines_of(path)
        for number, row in enumerate(rows, start=1):
            if row == old:
                battery.add("derivation_written_by_hand", path, number, old, new)
                break


# --------------------------------------------------------------------------
# Class 4: a constant that governs the drawing.
# --------------------------------------------------------------------------
def gen_figure_governing_number(battery):
    rows = lines_of("src/figure.py")
    for number, row in enumerate(rows, start=1):
        match = re.match(r"^([A-Z_]+) = (\d+)$", row)
        if match:
            battery.add("figure_governing_number", "src/figure.py", number,
                        row, "%s = %s" % (match.group(1), bump(match.group(2))))


# --------------------------------------------------------------------------
# Class 5: the committed figure no longer matches the data.
# --------------------------------------------------------------------------
def gen_figure_gone_stale(battery):
    path = "figures/digit_frequencies.svg"
    rows = lines_of(path)
    for number, row in enumerate(rows, start=1):
        match = re.search(r"(\d+)</text>", row)
        if match:
            old = match.group(1) + "</text>"
            battery.add("figure_gone_stale", path, number, old,
                        bump(match.group(1)) + "</text>")


# --------------------------------------------------------------------------
# Class 6: a frozen value is edited in the claim table.
# --------------------------------------------------------------------------
def gen_frozen_value_edited(battery):
    rows = lines_of("src/frozen_claims.py")
    for claim in fc.CLAIMS:
        start = None
        for number, row in enumerate(rows, start=1):
            if 'Claim("%s"' % claim.id in row:
                start = number
                break
        if start is None:
            continue
        needle = '"%s", "%s"' % (claim.text, claim.fmt)
        for number in range(start, min(start + 4, len(rows) + 1)):
            if needle in rows[number - 1]:
                battery.add("frozen_value_edited", "src/frozen_claims.py", number,
                            needle, '"%s", "%s"' % (bump(claim.text), claim.fmt))
                break


# --------------------------------------------------------------------------
# Class 7: a reported result is embedded in the source as a dead assignment.
# --------------------------------------------------------------------------
EMBEDDING_MODULES = ("src/stats_path_a_series.py", "src/stats_path_b_exact.py")


def gen_result_embedded_in_code(battery):
    values = []
    for claim in fc.CLAIMS:
        if claim.kind == fc.COMPUTED_DUAL and claim.text not in values:
            values.append(claim.text)
    for path in EMBEDDING_MODULES:
        rows = lines_of(path)
        anchor = None
        for number, row in enumerate(rows, start=1):
            if row.startswith("N_CATEGORIES = "):
                anchor = number
                break
        for value in values:
            row = rows[anchor - 1]
            battery.add("result_embedded_in_code", path, anchor, row,
                        row + "\n\n#: Copy of a reported result, kept next to the code.\n"
                        "CACHED_REPORTED_VALUE = " + value)


# --------------------------------------------------------------------------
# Class 8: a forbidden phrase is reintroduced on a watched surface.
# --------------------------------------------------------------------------
def gen_forbidden_phrase(battery):
    for surface in fp.WATCHED_SURFACES:
        rows = lines_of(surface)
        anchor = len(rows)
        for phrase in fp.FORBIDDEN:
            row = rows[anchor - 1]
            battery.add("forbidden_phrase", surface, anchor, row,
                        row + "\n\nA closing remark: " + phrase + " here.")


# --------------------------------------------------------------------------
# Class 9: front matter drifts on one surface.
# --------------------------------------------------------------------------
def gen_front_matter_drift(battery):
    perturbations = {
        "title": ((": A Minimal Stasis Artifact", ""), ("pi", "Pi")),
        "author": (("í", "i"), (" Hurtado", "")),
        "year": ((fm.YEAR, bump(fm.YEAR)),),
    }
    values = {"title": fm.TITLE, "author": fm.AUTHOR, "year": fm.YEAR}
    for field in ("title", "author", "year"):
        value = values[field]
        for surface in fm.FRONT_MATTER_SURFACES:
            rows = lines_of(surface)
            for number, row in enumerate(rows, start=1):
                if value not in row:
                    continue
                for old_part, new_part in perturbations[field]:
                    if old_part in row:
                        battery.add("front_matter_drift", surface, number,
                                    old_part, new_part)


# --------------------------------------------------------------------------
# Classes 10, 11, 13: the input data.
# --------------------------------------------------------------------------
PATH_A_RETURN = "    return decimals[:n]"
PATH_B_RETURN = "    return [int(c) for c in decimals[:n]]"

DATA_SITES = (("src/data_path_a_spigot.py", PATH_A_RETURN, "decimals[:n]"),
              ("src/data_path_b_machin.py", PATH_B_RETURN,
               "[int(c) for c in decimals[:n]]"))


def _data_line(path, old):
    for number, row in enumerate(lines_of(path), start=1):
        if row == old:
            return number
    return None


def gen_data_corrupted(battery, rng, sample_size):
    digits = fc.digits_path_a()
    positions = sorted(rng.sample(range(len(digits)), sample_size))
    path, old, expr = DATA_SITES[0]
    line = _data_line(path, old)
    for position in positions:
        battery.add("data_corrupted", path, line, old,
                    "    corrupted = %s\n"
                    "    corrupted[%d] = (corrupted[%d] + 1) %% 10\n"
                    "    return corrupted" % (expr, position, position))


def gen_data_truncated(battery):
    for path, old, expr in DATA_SITES:
        line = _data_line(path, old)
        battery.add("data_truncated", path, line, old,
                    "    return (%s)[:-1]" % expr)
        battery.add("data_truncated", path, line, old,
                    "    return (%s) + [0]" % expr)


def gen_permutation(battery, rng, sample_size):
    digits = fc.digits_path_a()
    candidates = [p for p in range(len(digits) - 1) if digits[p] != digits[p + 1]]
    positions = sorted(rng.sample(candidates, sample_size))
    path, old, expr = DATA_SITES[0]
    line = _data_line(path, old)
    for position in positions:
        battery.add("permutation_no_statistical_effect", path, line, old,
                    "    corrupted = %s\n"
                    "    corrupted[%d], corrupted[%d] = corrupted[%d], corrupted[%d]\n"
                    "    return corrupted" % (expr, position, position + 1,
                                              position + 1, position))


# --------------------------------------------------------------------------
# Class 12: the negative control.
# --------------------------------------------------------------------------
PROSE_CONTROL_LINES = (
    ("paper.md", "The data are computed, not downloaded.",
     "The data are computed here, not downloaded."),
    ("paper.md", "There is nothing here.", "There is little here."),
    ("README.md", "That is the whole thing.", "That is the entire thing."),
    ("README.md", "Finding out that something went stale is the point.",
     "Finding out that something went stale is the whole point."),
)


def gen_nonnumeric_text_change(battery):
    modules = []
    for folder in ("src", "checks"):
        directory = os.path.join(SUBJECT, folder)
        for name in sorted(os.listdir(directory)):
            if name.endswith(".py"):
                modules.append("%s/%s" % (folder, name))
    for rel in modules:
        rows = lines_of(rel)
        for number, row in enumerate(rows, start=1):
            stripped = row.strip()
            if stripped.startswith("#") and not stripped.startswith("#!") \
                    and len(stripped) > 12:
                battery.add("nonnumeric_text_change", rel, number, row,
                            row + " Reviewed.")
                break
    for rel, old, new in PROSE_CONTROL_LINES:
        for number, row in enumerate(lines_of(rel), start=1):
            if old in row:
                battery.add("nonnumeric_text_change", rel, number, old, new)
                break


# --------------------------------------------------------------------------
# Class 14: a real change to the computation that moves no published value.
# --------------------------------------------------------------------------
def _renders_identically(candidate):
    """Apply a candidate to a throwaway copy and ask whether anything moved.

    This is the filter that makes the class honest. A candidate is an instance
    of `silent_propagation` only if, after it is applied, every frozen claim
    still renders to exactly the string it rendered before. Whether an edit is
    silent is therefore measured, not asserted by whoever wrote the list.

    Returns (is_silent, what moved).
    """
    import shutil
    import subprocess
    import tempfile
    _name, relative, old, new, _why = candidate
    workspace = tempfile.mkdtemp(prefix="silent_")
    try:
        sandbox = os.path.join(workspace, "subject")
        shutil.copytree(SUBJECT, sandbox,
                        ignore=lambda _d, names: [n for n in names
                                                  if n in ("__pycache__", ".git")])
        path = os.path.join(sandbox, *relative.split("/"))
        with io.open(path, encoding="utf-8") as handle:
            text = handle.read()
        if text.count(old) != 1:
            return False, "the target text occurs %d times" % text.count(old)
        with io.open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text.replace(old, new, 1))
        probe = (
            "import sys; sys.path.insert(0, '.')\n"
            "from src import frozen_claims as f\n"
            "d = f.digits_path_a(); va, _ = f.analyse_path_a(d)\n"
            "e = f.digits_path_b(); vb, _ = f.analyse_path_b(e)\n"
            "for c in f.CLAIMS:\n"
            "    if c.kind != f.COMPUTED_DUAL: continue\n"
            "    print(c.id, f.render(va[c.id], c.fmt), f.render(vb[c.id], c.fmt))\n")
        done = subprocess.run([sys.executable, "-c", probe], cwd=sandbox,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              universal_newlines=True)
        if done.returncode != 0:
            return False, "the analysis no longer runs"
        moved = []
        for row in done.stdout.strip().split("\n"):
            parts = row.split()
            if len(parts) != 3:
                continue
            claim_id, rendered_a, rendered_b = parts
            baseline = _BASELINE_RENDERS.get(claim_id)
            if rendered_a != baseline or rendered_b != baseline:
                moved.append(claim_id)
        return (not moved), ", ".join(sorted(set(moved)))
    finally:
        import shutil as _s
        _s.rmtree(workspace, ignore_errors=True)


def _baseline_renders():
    values, _counts = fc.analyse_path_a(fc.digits_path_a())
    return {claim.id: fc.render(values[claim.id], claim.fmt)
            for claim in fc.CLAIMS if claim.kind == fc.COMPUTED_DUAL}


_BASELINE_RENDERS = {}

#: Candidates rejected by the filter, with the reason, reported alongside the
#: battery so that a rejection is visible rather than silently absent.
REJECTED_SILENT_CANDIDATES = []


def gen_silent_propagation(battery):
    global _BASELINE_RENDERS
    _BASELINE_RENDERS = _baseline_renders()
    del REJECTED_SILENT_CANDIDATES[:]
    for candidate in phase5.SILENT_PROPAGATION_CANDIDATES:
        name, relative, old, new, _why = candidate
        silent, moved = _renders_identically(candidate)
        if not silent:
            REJECTED_SILENT_CANDIDATES.append((name, moved))
            continue
        line = None
        for number, row in enumerate(lines_of(relative), start=1):
            if old in row:
                line = number
                break
        battery.add("silent_propagation", relative, line, old, new)


# --------------------------------------------------------------------------
# Class 15: a sentence in the manuscript that no claim backs.
# --------------------------------------------------------------------------
def gen_unsupported_claim(battery):
    rows = lines_of("paper.md")
    for heading in MANUSCRIPT_SECTIONS:
        first, last = section_line_range("paper.md", heading)
        anchor = None
        for number in range(last - 1, first - 1, -1):
            if rows[number - 1].strip():
                anchor = number
                break
        for value in phase5.UNSUPPORTED_VALUES:
            row = rows[anchor - 1]
            battery.add("unsupported_claim", "paper.md", anchor, row,
                        row + "\n\nA further quantity of interest here is "
                        + value + ", reported for completeness.")


#: Declared sample sizes for the two classes that cannot be enumerated
#: exhaustively without multiplying the battery by a thousand.
SAMPLE_DATA_CORRUPTED = 30
SAMPLE_PERMUTATION = 20


def build():
    rng = random.Random(taxonomy.SEED)
    battery = Battery()
    gen_manuscript_number_edited(battery)
    gen_constant_copied_to_prose(battery)
    gen_derivation_written_by_hand(battery)
    gen_figure_governing_number(battery)
    gen_figure_gone_stale(battery)
    gen_frozen_value_edited(battery)
    gen_result_embedded_in_code(battery)
    gen_forbidden_phrase(battery)
    gen_front_matter_drift(battery)
    gen_data_corrupted(battery, rng, SAMPLE_DATA_CORRUPTED)
    gen_data_truncated(battery)
    gen_permutation(battery, rng, SAMPLE_PERMUTATION)
    gen_nonnumeric_text_change(battery)
    # Phase 5. Added last, and consuming no randomness, so that every sampled
    # class above draws exactly what it drew in the runs already published.
    gen_silent_propagation(battery)
    gen_unsupported_claim(battery)
    return battery


if __name__ == "__main__":
    b = build()
    counts = {}
    for mutant in b.mutants:
        counts[mutant["cls"]] = counts.get(mutant["cls"], 0) + 1
    for cls in sorted(counts):
        print("%-38s %4d" % (cls, counts[cls]))
    print("%-38s %4d" % ("TOTAL", len(b.mutants)))
    print("rejected as duplicates: %d, rejected as unanchored: %d"
          % (b.rejected_duplicates, b.rejected_unanchored))
