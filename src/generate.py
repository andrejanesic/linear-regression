import random

def generate(m: int) -> list[tuple[float, float]]:
    """
    Generate m random data points for linear regression.
    :param m: int, number of data points
    :return: list[tuple[float, float]], data points
    """
    assert m > 0

    slope = random.random() * 10
    intercept = random.random() * 10
    x_min = random.randint(-100, 100)
    x_max = x_min + random.randint(100, 200)

    xs = sorted([random.random() for _ in range(m)])
    xs = [x * (x_max - x_min) + x_min for x in xs]
    ys = [intercept + slope * x for x in xs]
    ys = [y + random.normalvariate(1, 0.5) * (x_max - x_min) for y in ys]

    return list(zip(xs, ys))