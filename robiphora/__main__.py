import argparse
import readline
from robiphora.opdl import KnowledgeBase
import robiphora.ccg as ccg


def predicate_words(predicate):
    s = set()
    for p in predicate.args:
        s |= predicate_words(p)
    if not predicate.args:
        s.add(predicate.name)
    return s


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pccg', metavar='g', type=argparse.FileType('r'),
                        required=True,
                        help='path to PCCG grammar definition')
    parser.add_argument('--opdl', metavar='k', type=argparse.FileType('r'),
                        required=True,
                        help='path to OPDL knowledgebase')
    args = parser.parse_args()

    print("Welcome to Robiphora!")
    print("Loading OPDL file {!r}...".format(args.opdl.name))
    kb = KnowledgeBase(args.opdl)
    print("Loading PCCG lexicon {!r}...".format(args.opdl.name))
    lexicon = list(ccg.parse(ccg.lex(args.pccg.read())))

    while True:
        try:
            line = input('ρ> ')
        except EOFError:
            print('\nbye!')
            sys.exit(0)
        except KeyboardInterrupt:
            print()
            continue
        words = line.replace(',', '').replace('.', '').split()
        parses = ccg.chartparse(line.split(), lexicon, None)
        if not parses:
            print("No parses generated for input... using words.")
        else:
            for parse in parses:
                print(parses[0][1])
            words = predicate_words(parses[0][1])
        for word in words:
            for obj in kb.objects.keys():
                p = kb.resolve(word, obj)
                print("{} resoves to object {} with probability {}"
                      .format(word, obj, p))

