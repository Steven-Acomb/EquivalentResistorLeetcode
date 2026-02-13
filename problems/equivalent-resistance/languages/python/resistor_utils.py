def series(a, b):
    return a + b


def parallel(a, b):
    return 1 / (1 / a + 1 / b)


def base_scf(index):
    return str(index)


def combine_scf(left, right, op):
    return f"({left}){op}({right})"


def evaluate_config(configuration, base_resistances):
    if configuration[0] != "(":
        return base_resistances[int(configuration)]

    parentheses = 1
    for i in range(1, len(configuration)):
        if configuration[i] == "(":
            parentheses += 1
        elif configuration[i] == ")":
            parentheses -= 1
        if parentheses == 0:
            start, end = _get_splits(configuration[i:])
            if start == -1:
                return evaluate_config(configuration[1:i], base_resistances)
            op = configuration[i + start : i + end]
            left = evaluate_config(configuration[1:i], base_resistances)
            right = evaluate_config(
                configuration[i + end + 1 : len(configuration) - 1],
                base_resistances,
            )
            return _FUNCTIONS[op](left, right)

    return -1


def _get_splits(config):
    op_symbols = ["+", "//"]
    for i in range(len(config)):
        for op in op_symbols:
            if config[i] == op[0]:
                return i, i + len(op)
    return -1, -1


_FUNCTIONS = {
    "+": lambda a, b: a + b,
    "//": lambda a, b: 1 / (1 / a + 1 / b),
}
