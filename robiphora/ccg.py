import re
from itertools import chain
from robiphora.opdl import match


class ControlToken:
    """
    Base class for all control tokens.
    """
    def __repr__(self):
        return self.__class__.__name__


T = {
    k: type(k, (ControlToken, ), dict(ControlToken.__dict__))
    for k in ("Comma", "Lambda", "Dot", "Define", "LParen", "RParen",
              "LBrack", "RBrack", "And", "Colon", "Whack", "Slash")}


class Production:
    pass


class Name(str, Production):
    def __repr__(self):
        return self

    def apply(self, pred, name):
        if name == self:
            return pred
        return self


class Type:
    def __init__(self, name):
        if not isinstance(name, str):
            raise TypeError("Name of Type must be a str")
        self.name = name

    def __repr__(self):
        return self.name


class TypeMissing(Type):
    def __init__(self, lhs, missing):
        if not isinstance(lhs, Type):
            raise TypeError("LHS of TypeMissing MUST be a Type")
        if not isinstance(missing, Type):
            raise TypeError("RHS of TypeMissing MUST be a Type")
        self.name = lhs
        self.missing = missing

    def __repr__(self):
        if isinstance(self.missing, TypeMissing):
            f = '{!r}{}({!r})'
        else:
            f = '{!r}{}{!r}'
        return f.format(self.name, self.op, self.missing)


class TypeMissingLeft(TypeMissing):
    op = '\\'


class TypeMissingRight(TypeMissing):
    op = '/'


class Abstraction(Production):
    def __init__(self, var, prod):
        if not isinstance(prod, Production):
            raise TypeError("prod must be a Production")
        if not isinstance(var, str):
            raise TypeError("var must be a str")
        self.var = var
        self.prod = prod

    def apply(self, pred, name=None):
        if name == self.var:
            return self
        if not name:
            name = self.var
            return self.prod.apply(pred, name=name)
        return Abstraction(self.var, self.prod.apply(pred, name))

    def __repr__(self):
        return 'λ{}.{!r}'.format(self.var, self.prod)


class Predicate(Production):
    def __init__(self, name, *args):
        self.name = name
        self.args = args

    def __repr__(self):
        return '{}({})'.format(self.name, ', '.join(map(repr, self.args)))

    def apply(self, pred, name):
        if not self.args:
            return self
        return Predicate(self.name, *(x.apply(pred, name) for x in self.args))


class And(Production):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return '{!r} Λ {!r}'.format(self.lhs, self.rhs)

    def apply(self, pred, name):
        return And(self.lhs.apply(pred, name), self.rhs.apply(pred, name))


class Definition:
    def __init__(self, word, typ, production, probdict=None, defaultprob=1.0):
        if probdict is None:
            probdict = {}
        if not isinstance(defaultprob, float):
            raise TypeError("defaultprob must be a float")
        if not isinstance(probdict, dict):
            raise TypeError("probdict must be a dict")
        if not isinstance(production, Production):
            raise TypeError("production is not a Production")
        if not isinstance(typ, Type):
            raise TypeError("typ is not a Type")
        if not isinstance(word, str):
            raise TypeError("word is not a str")
        self.word = word
        self.typ = typ
        self.production = production
        self.probdict = probdict
        self.defaultprob = defaultprob

    def __repr__(self):
        if self.probdict or self.defaultprob != 1.0:
            probrepr = ' [{}]'.format(
                ', '.join(chain(
                    ('{} {}'.format(k, v) for k, v in self.probdict.items()),
                    (str(self.defaultprob), )
                        if self.defaultprob != 1.0
                        else ())))
        else:
            probrepr = ''
        return '{!r} := {!r}{} : {!r}'.format(
                self.word,
                self.typ,
                probrepr,
                self.production)


class PartialPredicate(list):
    def __repr__(self):
        return 'PartialPredicate({})'.format(super().__repr__())


class DefaultProbability(float):
    def __repr__(self):
        return 'DefaultProbability({})'.format(super().__repr__())


class ProbabilityRelation(dict):
    def __repr__(self):
        return 'ProbabilityRelation({})'.format(super().__repr__())


tokens_p = re.compile(r'''
    \s*(?:  (?P<control>
                (?P<Comma>,)
            |   (?P<Lambda>λ)
            |   (?P<Dot>\.)
            |   (?P<Define>:=)
            |   (?P<LParen>\()
            |   (?P<RParen>\))
            |   (?P<LBrack>\[)
            |   (?P<RBrack>\])
            |   (?P<And>Λ)
            |   (?P<Colon>:)
            |   (?P<Whack>\\)
            |   (?P<Slash>/)
            )
       |    (?P<name>[^0-9/\\\s().\[\]:=,Λ]+)
       |    (?P<number>[01](\.[0-9]*)?)
       )\s*''', re.VERBOSE)


def lex(code):
    last_end = 0
    for m in tokens_p.finditer(code):
        if m.start() != last_end:
            raise SyntaxError("malformed input")
        if m.group('control'):
            keyset = {k for k, v in m.groupdict().items()
                      if k != 'control' and v}
            assert len(keyset) == 1 or print(keyset)
            yield T[keyset.pop()]()
        elif m.group('name'):
            yield Name(m.group('name'))
        elif m.group('number'):
            yield float(m.group('number'))
        last_end = m.end()
    if last_end != len(code):
        raise SyntaxError("malformed input")


def parse(tokens, debug=False):
    tokens = iter(tokens)
    stack = []
    lookahead = next(tokens)
    typectx = False
    while True:
        if debug:
            print(stack, '|', lookahead)
        if match(stack, [T['Define']]):
            typectx = True
            # Shift
            stack.append(lookahead)
            lookahead = next(tokens)
        elif match(stack, [T['Colon']]):
            typectx = False
            # Shift
            stack.append(lookahead)
            lookahead = next(tokens)
        elif match(stack, [T['LBrack']]):
            typectx = False
            # Shift
            stack.append(lookahead)
            lookahead = next(tokens)
        elif match(stack, [Name]) and typectx:
            n = stack.pop()
            stack.append(Type(n))
        elif match(stack, (T['LParen'], Type, T['RParen'])):
            # Reduce by Type -> ( Type )
            _, t, _ = (stack.pop() for _ in range(3))
            stack.append(t)
        elif match(stack, (Type, T['Whack'], Type)):
            # Reduce by TypeMissingLeft -> Type \ Type
            rhs, _, lhs = (stack.pop() for _ in range(3))
            stack.append(TypeMissingLeft(lhs, rhs))
        elif match(stack, (Type, T['Slash'], Type)):
            # Reduce by TypeMissingRight -> Type / Type
            rhs, _, lhs = (stack.pop() for _ in range(3))
            stack.append(TypeMissingRight(lhs, rhs))
        elif match(stack, [Name, float, T['RBrack']]):
            stack.pop()
            p, n = (stack.pop() for _ in range(2))
            default = DefaultProbability(1.0)
            r = ProbabilityRelation({n: p})
            stack.append(r)
            stack.append(default)
        elif match(stack, [float, T['RBrack']]):
            stack.pop()
            default = DefaultProbability(stack.pop())
            r = ProbabilityRelation()
            stack.append(r)
            stack.append(default)
        elif match(stack,
                   [Name,
                    float,
                    T['Comma'],
                    ProbabilityRelation,
                    DefaultProbability]):
            default, r, _, p, n = (stack.pop() for _ in range(5))
            r[n] = p
            stack.append(r)
            stack.append(default)
        elif (match(stack, (T['Lambda'], Name, T['Dot'], Production))
              and not isinstance(lookahead, ControlToken)):
            # Reduce by Abstraction -> λ Name . Production
            p, _, x, _ = (stack.pop() for _ in range(4))
            stack.append(Abstraction(x, p))
        elif (match(stack, (Production, T['And'], Production))
              and not isinstance(lookahead, ControlToken)):
            # Reduce by And -> Production Λ Production
            rhs, _, lhs = (stack.pop() for _ in range(3))
            stack.append(And(lhs, rhs))
        elif match(stack, [T['RParen']]) and not typectx:
            # Reduce by PartialPredicate -> )
            stack.pop()
            stack.append(PartialPredicate())
        elif match(stack, [Production, PartialPredicate]):
            # Reduce by PartialPredicate -> Production PartialPredicate
            pp, prod = (stack.pop() for _ in range(2))
            pp.append(prod)
            stack.append(pp)
        elif match(stack, [Production, T['Comma'], PartialPredicate]):
            # Reduce by PartialPredicate -> Production , PartialPredicate
            pp, _, prod = (stack.pop() for _ in range(3))
            pp.append(prod)
            stack.append(pp)
        elif match(stack, (Name, T['LParen'], PartialPredicate)):
            # Reduce by Predicate -> Name ( PartialPredicate
            pp, _, name = (stack.pop() for _ in range(3))
            stack.append(Predicate(name, *reversed(pp)))
        elif match(stack,
                   [Name,
                    T['Define'],
                    Type,
                    T['LBrack'],
                    ProbabilityRelation,
                    DefaultProbability,
                    T['Colon'],
                    Production]) and not isinstance(lookahead, ControlToken):
            production, _, default, r, _, typ, _, word = (
                stack.pop() for _ in range(8))
            yield Definition(word, typ, production, r, default)
        elif match(stack,
                   [Name,
                    T['Define'],
                    Type,
                    T['Colon'],
                    Production]) and not isinstance(lookahead, ControlToken):
            production, _, typ, _, word = (
                stack.pop() for _ in range(5))
            yield Definition(word, typ, production)
        else:
            # Shift
            if lookahead is None:
                break
            try:
                stack.append(lookahead)
                lookahead = next(tokens)
            except StopIteration:
                lookahead = None
    if stack:
        raise SyntaxError("incomplete parse")
