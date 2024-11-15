from typing import Callable
from .expr import *

def J(f: Callable[[Expr], Expr], xs: list[Expr], ys: list[Expr]) -> Expr:
    assert len(xs) == len(ys)
    return Mul(Div(1, Mul(2, len(ys))), Add(*[Pow(Sub(Var('y', ys[i]), f(xs[i])), 2) for i in range(len(ys))]))