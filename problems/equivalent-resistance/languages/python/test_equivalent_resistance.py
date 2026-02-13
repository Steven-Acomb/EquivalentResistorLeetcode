import atexit
from solution import Solution
from resistor_utils import evaluate_config

DELTA = 1e6
points = 0


def _show_points():
    print(f"EQUIVALENT_RESISTANCE POINTS = {points:.1f} of 8.0")


atexit.register(_show_points)


def example_base_resistances():
    return [
        1, 1.5, 2.7, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5,
        8.2, 9.1, 10, 11, 12, 13, 15, 16, 18, 20,
        22, 24, 27, 30, 33, 36, 39, 43, 47, 51,
        56, 62, 68, 75, 82, 91, 100, 110, 120, 130,
        150, 160, 180, 200, 220, 240, 270, 300, 330, 360,
        390, 430, 470, 510, 560, 620, 680, 750, 820, 910,
        1000, 1100, 1200, 1300, 1500, 1600, 1800, 2000, 2200, 2400,
        2700, 3000, 3300, 3600, 3900, 4500, 4700, 5100, 5600, 6200,
        7500, 8200, 9100, 10000, 11000, 12000, 13000, 15000, 16000, 18000,
        20000, 22000, 24000, 27000, 30000, 33000, 36000, 39000, 43000, 47000,
        51000, 56000, 62000, 68000, 75000, 82000, 91000, 100000, 110000, 120000,
        130000, 150000, 160000, 180000, 200000, 220000, 240000, 270000, 300000, 330000,
        360000, 390000, 430000, 470000, 510000, 560000, 620000, 680000, 750000, 820000, 910000,
        1000000, 1100000, 1200000, 1300000, 1500000, 1600000, 1800000, 2000000, 2100000, 2200000,
        2400000, 2700000, 3000000, 3300000, 3600000, 3900000, 4700000, 5600000, 6800000, 8200000,
        10000000,
    ]


def test_1():
    global points
    base_resistances = example_base_resistances()
    solution = Solution()
    config = "((0)//(4))+((3)//(2))"  # ~= 2.48313
    max_resistors = 4
    expected = evaluate_config(config, base_resistances)
    actual = evaluate_config(
        solution.approximate(base_resistances, expected, max_resistors),
        base_resistances,
    )
    assert abs(expected - actual) <= expected / DELTA
    points += 1.0


def test_2():
    global points
    base_resistances = [1, 2]
    solution = Solution()
    config = "((1)+((1)//((1)+((0)//(1)))))"  # ~= 3.142857142857143
    max_resistors = 5
    expected = evaluate_config(config, base_resistances)
    actual = evaluate_config(
        solution.approximate(base_resistances, expected, max_resistors),
        base_resistances,
    )
    assert abs(expected - actual) <= expected / DELTA
    points += 1.0


def test_3():
    global points
    base_resistances = [1, 1000]
    solution = Solution()
    config = "(0)//((0)//((0)//((0)//((0)//((0)//((0)//(0)))))))"  # ~= 0.125
    max_resistors = 8
    expected = evaluate_config(config, base_resistances)
    actual = evaluate_config(
        solution.approximate(base_resistances, 0, max_resistors),
        base_resistances,
    )
    assert abs(expected - actual) <= expected / DELTA
    points += 1.0


def test_4():
    global points
    base_resistances = [0.1, 1]
    solution = Solution()
    config = "(1)+((1)+((1)+((1)+((1)+((1)+((1)+(1)))))))"  # ~= 8
    max_resistors = 8
    expected = evaluate_config(config, base_resistances)
    actual = evaluate_config(
        solution.approximate(base_resistances, float("inf"), max_resistors),
        base_resistances,
    )
    assert abs(expected - actual) <= expected / DELTA
    points += 1.0


def test_5():
    global points
    base_resistances = [
        336, 420, 480, 560, 630, 672,
        720, 840, 960, 1008, 1050, 1120,
        1200, 1260, 1344, 1400, 1440, 1680,
        1960, 2016, 2100, 2240, 2352, 2520,
        2688, 2800, 2940, 3360, 3920, 4200,
        4480, 5040, 5880, 6720, 8400,
    ]
    solution = Solution()
    config = "(20)+((25)//(28))"  # ~= 3733.33 (11200/3)
    max_resistors = 3
    expected = evaluate_config(config, base_resistances)
    actual = evaluate_config(
        solution.approximate(base_resistances, expected, max_resistors),
        base_resistances,
    )
    assert abs(expected - actual) <= expected / DELTA
    points += 1.0


def test_6():
    global points
    base_resistances = [1680]
    solution = Solution()
    config = "(0)+((0)+((0)//((0)//((0)//((0)//((0)+(0)))))))"  # ~= 3733.33 (11200/3)
    max_resistors = 8
    expected = evaluate_config(config, base_resistances)
    actual = evaluate_config(
        solution.approximate(base_resistances, expected, max_resistors),
        base_resistances,
    )
    assert abs(expected - actual) <= expected / DELTA
    points += 1.0


def test_7():
    global points
    base_resistances = [13]
    solution = Solution()
    config = "(0)//((0)//((0)//((0)//((0)//((0)//((0)//((0)//((0)//((0)//((0)//((0)//(0))))))))))))"  # = 1.0
    max_resistors = 13
    expected = evaluate_config(config, base_resistances)
    actual = evaluate_config(
        solution.approximate(base_resistances, expected, max_resistors),
        base_resistances,
    )
    assert abs(expected - actual) <= expected / DELTA
    points += 1.0


def test_8():
    global points
    base_resistances = [17]
    solution = Solution()
    config = "((0)//(0))+((0)//((0)+((0)//((0)+((0)//((0)+((0)//(0))))))))"  # = 19.0
    max_resistors = 10
    expected = evaluate_config(config, base_resistances)
    actual = evaluate_config(
        solution.approximate(base_resistances, expected, max_resistors),
        base_resistances,
    )
    assert abs(expected - actual) <= expected / DELTA
    points += 1.0


