from .expr import *

def f(xs: list[Expr], thetas: list[Expr]) -> Expr:
    assert len(xs) == len(thetas)
    return Add(*[Mul(thetas[i], xs[i]) for i in range(len(xs))])