"""
Object Property Definition Language
===================================

:Author: Jack Rosenthal

This module contains utilities for using OPDL in Python.
"""
import re
import os


class CompleteExpression:
    pass


class SExpression(CompleteExpression):
    def __init__(self, args, kwargs):
        self.args = list(args)
        self.kwargs = dict(kwargs)

    def __repr__(self):
        return '({}{}{})'.format(
            ' '.join(map(repr, self.args)),
            ' ' if self.args and self.kwargs else '',
            ' '.join(':{} {!r}'.format(k, v) for k, v in self.kwargs.items()))


class PartialSE:
    def __init__(self, args=None, kwargs=None):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return SExpression.__repr__(self)[1:]


class Symbol(CompleteExpression, str):
    def __repr__(self):
        return str(self)


class String(CompleteExpression, str):
    def __repr__(self):
        r = super().__repr__()
        if r.startswith("'"):
            return '"{}"'.format(r[1:-1].replace('"', '\\"')
                                        .replace("\\'", "'"))
        return r


class LParen:
    def __repr__(self):
        return '('


class KeywordArgName:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return ':{}'.format(self.name)


class KeywordArg:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return ':{} {!r}'.format(self.name, self.value)


tokenizer_p = re.compile(r'''
    \s*(?:  (?P<control>\(|\))
       |    (?:;[^\n]*(?:\n|$))
       |    (?P<string>"(?:\\.|[^\\"])*")
       |    (?P<kwarg>:[^()"'\s;]+)
       |    (?P<symbol>[^()"'\s;]+)
       )\s*''', re.VERBOSE | re.DOTALL)

control_classes = {
    '(': LParen,
    ')': PartialSE,
}


def lex(code):
    """
    Lexically analyze the input.
    """
    last_end = 0
    for m in tokenizer_p.finditer(code):
        if m.start() != last_end:
            raise SyntaxError("malformed input: {!r}".format(
                code[last_end:m.start()]))
        last_end = m.end()
        if m.group('control'):
            yield control_classes[m.group('control')]()
        elif m.group('kwarg'):
            yield KeywordArgName(m.group('kwarg')[1:])
        elif m.group('symbol'):
            yield Symbol(m.group('symbol'))
        elif m.group('string'):
            yield String(m.group('string')[1:-1])
    if last_end != len(code):
        raise SyntaxError("malformed tokens at end of input")


def match(stack, types):
    if len(stack) < len(types):
        return False
    for elem, t in zip(reversed(stack), reversed(types)):
        if not isinstance(elem, t):
            return False
    return True


def separse(tokens):
    tokens = iter(tokens)
    stack = []
    while True:
        if match(stack, [KeywordArgName, CompleteExpression]):
            e, k = (stack.pop() for _ in range(2))
            stack.append(KeywordArg(k.name, e))
        elif match(stack, [KeywordArg, PartialSE]):
            e, k = (stack.pop() for _ in range(2))
            if e.args:
                raise SyntaxError('keywords must come at end of expression')
            if k.name in e.kwargs.keys():
                raise SyntaxError('{} defined twice'.format(k.name))
            e.kwargs[k.name] = k.value
            stack.append(e)
        elif match(stack, [CompleteExpression, PartialSE]):
            e, s = (stack.pop() for _ in range(2))
            e.args.append(s)
            stack.append(e)
        elif match(stack, [LParen, PartialSE]):
            e, p = (stack.pop() for _ in range(2))
            stack.append(SExpression(e.args[::-1], e.kwargs))
        elif len(stack) == 1 and isinstance(stack[0], SExpression):
            yield stack.pop()
        else:
            try:
                stack.append(next(tokens))
            except StopIteration:
                break
    if stack:
        raise SyntaxError('parse error')


class OPDLData:
    """
    Base class for constructs in OPDL.
    """
    def __init__(self, name, **kwargs):
        self.name = name
        for attrname, _ in self.__class__.namepairs:
            setattr(self,
                    attrname,
                    set(kwargs.get(attrname, SExpression([], {})).args))

    @classmethod
    def from_se(cls, se):
        o = cls(name=se.args[1])
        for attrname, argname in cls.namepairs:
            if argname in se.kwargs.keys():
                setattr(o, attrname, set(se.kwargs[argname].args))
        return o

    def __repr__(self):
        return '{}({!r}, {})'.format(
            self.__class__.__name__,
            self.name,
            ', '.join(
                '{}={!r}'.format(k, getattr(self, k))
                for k, _ in self.__class__.namepairs))


class Type(OPDLData):
    namepairs = (("bases", "bases"),
                 ("antibases", "antibases"),
                 ("adjectives", "provides-adjectives"),
                 ("pronouns", "pronouns"),
                 ("nouns", "nouns"))


class Object(OPDLData):
    namepairs = (("types", "type"), )


class KnowledgeBase:
    def __init__(self, init_load=None):
        self.objects = {}
        self.types = {}
        if init_load:
            self.load(init_load)

    def load(self, code, path=None):
        if path is None and hasattr(code, "name"):
            path = os.path.dirname(code.name)
        if hasattr(code, "read"):
            code = code.read()
        for se in separse(lex(code)):
            if se.args[0] == 'import':
                if path is not None:
                    with open("{}/{}".format(path, se.args[1])) as f:
                        self.load(f)
                else:
                    raise TypeError("import only supported on named files")
            elif se.args[0] == 'object':
                self.objects[se.args[1]] = Object.from_se(se)
            elif se.args[0] == 'type':
                self.types[se.args[1]] = Type.from_se(se)
            else:
                raise SyntaxError("Unknown OPDL data: {!r}".format(se.args[0]))
