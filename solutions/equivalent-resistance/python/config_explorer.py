"""
Scratchpad for exploring all possible SERIES-PARALLEL resistor configurations.

Generates every distinct series-parallel configuration of up to N identical
resistors, showing how each was built from smaller sub-configurations.

IMPORTANT: This only enumerates series-parallel configurations — circuits that
can be recursively decomposed into two sub-circuits combined with series or
parallel. This is COMPLETE for series-parallel (that recursive decomposition is
the *definition* of series-parallel), but it MISSES non-series-parallel
topologies such as:
  - Wheatstone bridge circuits (minimum 5 resistors)
  - Any circuit whose graph has K4 (complete graph on 4 nodes) as a minor

A series-parallel graph is exactly one with no K4 minor. Non-series-parallel
circuits require Kirchhoff's laws or delta-wye transforms to evaluate and
cannot be represented in SCF format.

For the full picture (all 2-connected graphs, not just series-parallel), see:
  - OEIS A174283 (includes bridges, diverges from series-parallel at n=5)
  - OEIS A337516 (general configurations including bridge + fork)
  - Gottlieb: https://cs.nyu.edu/~gottlieb/tr/overflow/2003-oct-3-more.html

Usage:
    PYTHONPATH=problems/equivalent-resistance/languages/python \
        python solutions/equivalent-resistance/python/config_explorer.py
"""

from resistor_utils import base_scf, combine_scf, evaluate_config, parallel, series

BASE_RESISTANCES = [1]
MAX_RESISTORS = 5
# PYTHONPATH=problems/equivalent-resistance/languages/python python /home/stephenacomb/Documents/Github_Projects/EquivalentResistorLeetcode/solutions/equivalent-resistance/python/config_explorer.py

# This is OEIS https://oeis.org/A048211
# also see: https://oeis.org/A174283
# also see: https://oeis.org/A337516
# all: https://oeis.org/A337517
# also all? https://oeis.org/A180414
# https://cs.nyu.edu/~gottlieb/tr/overflow/2003-oct-3-more.html


def generate_all_configs(base_resistances, max_resistors):
    """
    Build all possible SERIES-PARALLEL configurations level by level.

    Returns a dict: configs[n] = list of (scf, value, description) tuples
    for configurations using exactly n resistors.

    Each configuration is either:
      - A single base resistor (n=1), or
      - Two sub-configurations combined with series or parallel (n>1),
        where the left uses k resistors and the right uses n-k.

    This recursive decomposition is the definition of a series-parallel circuit,
    so this enumeration is COMPLETE for series-parallel but does not produce any
    non-series-parallel topologies (bridges, etc.). The distinct value counts
    match OEIS A048211 for the single-base-resistance case.
    """
    configs = {}

    # Level 1: single base resistors
    configs[1] = []
    for i, r in enumerate(base_resistances):
        scf = base_scf(i)
        configs[1].append((scf, r, f"base resistor index {i} = {r}Ω"))

    # Levels 2..max_resistors: combine sub-configurations
    for n in range(2, max_resistors + 1):
        configs[n] = []
        seen_values = set()

        # Split n resistors into k (left) and n-k (right)
        for k in range(1, n):
            j = n - k
            for scf_a, val_a, desc_a in configs[k]:
                for scf_b, val_b, desc_b in configs[j]:
                    # Series combination
                    s_val = series(val_a, val_b)
                    s_scf = combine_scf(scf_a, scf_b, "+")
                    s_desc = f"series({val_a}, {val_b}) = {s_val}  [{k}+{j} resistors]"
                    if s_val not in seen_values:
                        configs[n].append((s_scf, s_val, s_desc))
                        seen_values.add(s_val)

                    # Parallel combination
                    if val_a > 0 and val_b > 0:
                        p_val = parallel(val_a, val_b)
                        p_scf = combine_scf(scf_a, scf_b, "//")
                        p_desc = f"parallel({val_a}, {val_b}) = {p_val}  [{k}+{j} resistors]"
                        if p_val not in seen_values:
                            configs[n].append((p_scf, p_val, p_desc))
                            seen_values.add(p_val)

        # Sort by value for readability
        configs[n].sort(key=lambda x: x[1])

    return configs


def print_configs(configs):
    for n in sorted(configs.keys()):
        print(f"\n{'='*70}")
        print(f"  {n} RESISTOR(S)  —  {len(configs[n])} distinct value(s)")
        print(f"{'='*70}")
        for scf, val, desc in configs[n]:
            print(f"\n  Value: {val}")
            print(f"  SCF:   {scf}")
            print(f"  Built: {desc}")


def print_summary(configs):
    print(f"\n{'='*70}")
    print(f"  SUMMARY: all achievable values by resistor count")
    print(f"{'='*70}")
    for n in sorted(configs.keys()):
        values = sorted(v for _, v, _ in configs[n])
        print(f"\n  n={n}: {values}")

    # Also show cumulative (best achievable with AT MOST n resistors)
    print(f"\n{'='*70}")
    print(f"  CUMULATIVE: all values achievable with <= N resistors")
    print(f"{'='*70}")
    all_values = set()
    for n in sorted(configs.keys()):
        for _, v, _ in configs[n]:
            all_values.add(v)
        print(f"\n  n<={n}: {sorted(all_values)}")


def count_topologies(max_resistors):
    """
    Count the number of distinct SERIES-PARALLEL circuit topologies (tree shape
    × operator assignment) for exactly n identical resistors.

    A topology here is a full binary tree with n leaves, where each internal
    node is labeled series or parallel. Two topologies that differ only by
    swapping the children of a commutative operator are counted separately
    (making this an upper bound on structurally distinct series-parallel
    topologies).

    This does NOT count non-series-parallel topologies (bridges, etc.) which
    are not representable as binary trees. Enumerating those requires
    enumerating 2-connected graphs — a harder graph theory problem.
    """
    # topo[n] = number of distinct topologies with exactly n resistors
    topo = {1: 1}
    for n in range(2, max_resistors + 1):
        count = 0
        for k in range(1, n):
            j = n - k
            # Each pair of sub-topologies can be combined 2 ways (series/parallel)
            count += topo[k] * topo[j] * 2
        topo[n] = count
    return topo


def print_counts(configs, topos):
    print(f"\n{'='*70}")
    print(f"  COUNTS: topologies vs distinct values for n identical resistors")
    print(f"{'='*70}")
    print(f"  {'n':>3}  {'topologies':>12}  {'distinct values':>16}  {'cumulative values':>18}")
    print(f"  {'---':>3}  {'----------':>12}  {'---------------':>16}  {'-----------------':>18}")
    cumulative = set()
    for n in sorted(configs.keys()):
        for _, v, _ in configs[n]:
            cumulative.add(v)
        t = topos.get(n, "?")
        v = len(configs[n])
        print(f"  {n:>3}  {t:>12}  {v:>16}  {len(cumulative):>18}")


if __name__ == "__main__":
    configs = generate_all_configs(BASE_RESISTANCES, MAX_RESISTORS)
    topos = count_topologies(MAX_RESISTORS)

    # Only print full detail for small n, otherwise just counts
    if MAX_RESISTORS <= 5:
        print_configs(configs)
        print_summary(configs)

    print_counts(configs, topos)
