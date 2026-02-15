"""
Scratchpad for exploring all possible resistor configurations.

Generates every distinct configuration of up to N identical resistors,
showing how each was built from smaller sub-configurations.

Usage:
    PYTHONPATH=problems/equivalent-resistance/languages/python \
        python solutions/equivalent-resistance/python/config_explorer.py
"""

from resistor_utils import base_scf, combine_scf, evaluate_config, parallel, series

BASE_RESISTANCES = [1]
MAX_RESISTORS = 10
# This is OEIS https://oeis.org/A048211
# also see: https://oeis.org/A174283
# also see: https://oeis.org/A337516
# all: https://oeis.org/A337517


def generate_all_configs(base_resistances, max_resistors):
    """
    Build all possible configurations level by level.

    Returns a dict: configs[n] = list of (scf, value, description) tuples
    for configurations using exactly n resistors.

    Each configuration is either:
      - A single base resistor (n=1), or
      - Two sub-configurations combined with series or parallel (n>1),
        where the left uses k resistors and the right uses n-k.
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
    Count the number of distinct circuit topologies (tree shape × operator
    assignment) for exactly n identical resistors.

    A topology is a full binary tree with n leaves, where each internal node
    is labeled series or parallel. Two topologies that differ only by swapping
    the children of a commutative operator are counted separately here (upper
    bound) — the distinct VALUE count from generate_all_configs is the real
    measure of how many meaningfully different configurations exist.
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
