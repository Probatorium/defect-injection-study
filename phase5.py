"""Phase 5: two new classes and one added ablation configuration.

Kept out of `taxonomy.py` on purpose. That module was committed as part of the
first preregistration and is evidence about what was declared before any data
existed; adding to it afterwards would weaken that for no gain. The same
reasoning put subject pinning in `subject.py`.

The eight configurations in `taxonomy.ABLATION_MODULES` are NOT touched, so
every rate already published stays comparable. One configuration is added here.
Adding one cannot change the result of any other.
"""

#: A ninth ablation configuration, isolating the one check that two competing
#: predictions disagree about. `check_50` is bundled into mechanism 1's ablation
#: by the original taxonomy; removing it alone says what it, and only it, holds.
EXTRA_ABLATION = {
    "2b manuscript number coverage alone": ("check_50_manuscript_coverage.py",),
}

#: Class 14. Each entry is one real change to the computation, paired with the
#: reason it is expected to leave every published value where it is. The list is
#: declared; whether each entry actually is silent is MEASURED, by the filter in
#: `generate.gen_silent_propagation`, not asserted here.
SILENT_PROPAGATION_CANDIDATES = (
    ("guard_digits_spigot", "src/data_path_a_spigot.py",
     "GUARD_DIGITS = 30", "GUARD_DIGITS = 45",
     "more guard digits computed and discarded by the bounded spigot"),
    ("guard_digits_machin", "src/data_path_b_machin.py",
     "GUARD_DIGITS = 20", "GUARD_DIGITS = 35",
     "more guard places carried through the fixed-point arithmetic"),
    ("spigot_array_slack", "src/data_path_a_spigot.py",
     "    length = 10 * n // 3 + 1", "    length = 10 * n // 3 + 3",
     "a longer remainder array; the emitted digits are the same digits"),
    ("series_threshold_a", "src/stats_path_a_series.py",
     "        if term <= total * 1e-17 or n > 100000:",
     "        if term <= total * 1e-13 or n > 100000:",
     "the incomplete gamma series stops four orders of magnitude earlier"),
    ("series_cap_a", "src/stats_path_a_series.py",
     "        if term <= total * 1e-17 or n > 100000:",
     "        if term <= total * 1e-17 or n > 50000:",
     "half the iteration cap on a series that converges long before either"),
    ("erfc_threshold_b", "src/stats_path_b_exact.py",
     "        if abs(contribution) <= abs(total) * 1e-18 or k > 10000:",
     "        if abs(contribution) <= abs(total) * 1e-14 or k > 10000:",
     "the erf series stops earlier; this is the candidate check_30 may catch"),
    ("erfc_cap_b", "src/stats_path_b_exact.py",
     "        if abs(contribution) <= abs(total) * 1e-18 or k > 10000:",
     "        if abs(contribution) <= abs(total) * 1e-18 or k > 5000:",
     "half the iteration cap on the erf series"),
    ("machin_scale_slack", "src/data_path_b_machin.py",
     "    scale = 10 ** (n + guard)", "    scale = 10 ** (n + guard + 5)",
     "five more fixed-point places; the digits sliced out are the same"),
    ("equivalent_fraction", "src/stats_path_b_exact.py",
     "    p = Fraction(1, N_CATEGORIES)", "    p = Fraction(2, 2 * N_CATEGORIES)",
     "an algebraically identical rational, built by a different route"),
    ("equivalent_sqrt", "src/stats_path_a_series.py",
     "    return math.erfc(abs(z) / math.sqrt(2.0))",
     "    return math.erfc(abs(z) * (2.0 ** -0.5))",
     "the same quantity through a different floating point path"),
)

#: Class 15. Values chosen so that none is the text of any frozen claim and none
#: occurs as a numeric literal anywhere in the package's code. Verified against
#: both before this list was written down.
UNSUPPORTED_VALUES = ("23", "58", "1729", "0.42", "3.19", "77")
