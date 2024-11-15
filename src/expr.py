from __future__ import annotations
from abc import ABC, abstractmethod

class Expr(ABC):

    __derivative_cache: dict[(str, str), Expr] = {}

    @abstractmethod
    def evaluate(self) -> float:
        pass

    def derivative(self, var: str) -> Expr:
        # TODO add cache
        return self._derivative(var)

    @abstractmethod
    def _derivative(self, var: str) -> Expr:
        pass
    
    def __add__(self, val):
        val = val if isinstance(val, Expr) else Const(val)
        return Add(self, val)
    
    def __sub__(self, val):
        val = val if isinstance(val, Expr) else Const(val)
        return Add(self, Mul(-1, val))
    
    def __mul__(self, val):
        val = val if isinstance(val, Expr) else Const(val)
        return Mul(self, val)

    def __pow__(self, val):
        val = val if isinstance(val, Expr) else Const(val)
        return Pow(self, val)

class Const(Expr):
    
    value: float

    def __init__(self, value: float):
        self.value = value

    def evaluate(self):
        return self.value

    def _derivative(self, var: str):
        return 0

    def __str__(self):
        return str(self.value)

class Var(Expr):

    name: str
    value: 'Expr' | float | None
    
    def __init__(self, name: str, value: 'Expr' | float | None = None):
        self.name = name
        self.value = value

    def evaluate(self) -> float:
        if self.value is None:
            raise ValueError(f'Variable {self.name} has no value assigned')
        if isinstance(self.value, Expr):
            return self.value.evaluate()
        return self.value

    def _derivative(self, var: str):
        if self.name != var:
            return Const(0)
        if (self.value is None):
            raise ValueError(f'Variable {self.name} has no value assigned')
        if isinstance(self.value, Expr):
            return self.value.derivative(var)
        return Const(1)

    def __str__(self):
        if isinstance(self.value, Expr):
            return str(self.value)
        return self.name
        
class MultiExpr(Expr):
    pass

class Add(MultiExpr):
    
    values: list[Expr]

    def __init__(self, *values: Expr | float):
        self.values = [v if isinstance(v, Expr) else Const(v) for v in values]
    
    def evaluate(self):
        res = sum([v.evaluate() for v in self.values])
        if isinstance(res, Expr):
            return res.evaluate()
        return res

    def _derivative(self, var: str):
        return Add(*[v.derivative(var) for v in self.values])

    def __str__(self):
        return ' + '.join([
            str(v) for v in self.values])

class Mul(MultiExpr):
        
    values: list[Expr]

    def __init__(self, *values: Expr | float):
        assert len(values) > 1
        self.values = [v if isinstance(v, Expr) else Const(v) for v in values]
    
    def evaluate(self):
        if len(self.values) == 2:
            return self.values[0].evaluate() * self.values[1].evaluate()
        return self.values[0].evaluate() * Mul(*self.values[1:]).evaluate()

    def _derivative(self, var: str):
        if (isinstance(self.values[0], Const)):
            return Mul(self.values[0],
                       self.values[1].derivative(var)
                       if len(self.values) == 2
                       else Mul(*self.values[1:]).derivative(var))
        if len(self.values) == 2:
            return Add(Mul(self.values[0].derivative(var), self.values[1]),
                       Mul(self.values[0], self.values[1].derivative(var)))
        return Add(Mul(self.values[0].derivative(var), Mul(*self.values[1:])),
                   Mul(self.values[0], Mul(*self.values[1:]).derivative(var)))

    def __str__(self):
        if (isinstance(self.values[0], Const) and abs(self.values[0].value) == 1):
            return ('-' if self.values[0] == -1 else '') + str(
                self.values[1]
                if len(self.values) == 2
                else Mul(*self.values[1:]))
        return ' * '.join([
            f'({v})' if isinstance(v, Add) else str(v)
            for v in self.values])

class Sub(Add):

    __a: Expr
    __b: Expr

    def __init__(self, a: Expr | float, b: Expr | float):
        super().__init__(a, Mul(-1, b))
        self.__a = a if isinstance(a, Expr) else Const(a)
        self.__b = b if isinstance(b, Expr) else Const(b)
    
    def __str__(self):
        return str(self.__a) + ' - ' + (('(' + str(self.__b) + ')') if isinstance(self.__b, MultiExpr) else str(self.__b))

class Pow(Expr):
    
    base: Expr
    exp: Expr

    def __init__(self, base_: Expr | float, exp: Expr | float):
        self.base = base_ if isinstance(base_, Expr) else Const(base_)
        self.exp = exp if isinstance(exp, Expr) else Const(exp)

    def evaluate(self):
        return self.base.evaluate() ** self.exp.evaluate()

    def _derivative(self, var: str):
        return Mul(self.exp, Pow(self.base, Sub(self.exp, 1)), self.base.derivative(var))
    
    def __str__(self):
        str_base = f'({self.base})' if isinstance(self.base, MultiExpr) else str(self.base)
        str_exp = f'({self.exp})' if isinstance(self.exp, MultiExpr) else str(self.exp)
        return f'{str_base}^{str_exp}'

class Div(Mul):
    
    __a: Expr
    __b: Expr

    def __init__(self, a: Expr | float, b: Expr | float):
        super().__init__(a, Pow(b, -1))
        self.__a = a if isinstance(a, Expr) else Const(a)
        self.__b = b if isinstance(b, Expr) else Const(b)

    def __str__(self):
        return (('(' + str(self.__a) + ')') if isinstance(self.__a, MultiExpr) else str(self.__a)) + \
                ' / ' + \
                (('(' + str(self.__b) + ')') if isinstance(self.__b, MultiExpr) else str(self.__b))