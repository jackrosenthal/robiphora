import argparse
import readline
import operator
import sys
import spacy
from functools import reduce
from robiphora.opdl import KnowledgeBase
import robiphora.ccg as ccg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pccg', metavar='g', type=argparse.FileType('r'),
                        required=False,
                        help='path to PCCG grammar definition')
    parser.add_argument('--opdl', metavar='k', type=argparse.FileType('r'),
                        required=True,
                        help='path to OPDL knowledgebase')
    parser.add_argument('--spacy-model',
            type=str,
            default='en_core_web_sm',
            help='spaCy model for tokenization')
    args = parser.parse_args()

    print("Welcome to Robiphora!")
    print("Loading OPDL file {!r}...".format(args.opdl.name))
    kb = KnowledgeBase(args.opdl)
    if args.pccg:
        print("Loading PCCG lexicon {!r}...".format(args.pccg.name))
        lexicon = list(ccg.parse(ccg.lex(args.pccg.read())))
    else:
        lexicon = None
    nlp = spacy.load(args.spacy_model)

    while True:
        try:
            line = input('ρ> ')
        except EOFError:
            print('\nbye!')
            sys.exit(0)
        except KeyboardInterrupt:
            print()
            continue
        if lexicon:
            words = line.replace(',', '').replace('.', '').split()
            parses = ccg.chartparse(words, lexicon, None)
            for parse in parses:
                print(parses[0][1])

        doc = nlp(line)
        noun_phrases = list(doc.noun_chunks)
        for np in noun_phrases:
            baseset = set()
            for tok in np:
                toktyp = spacy.explain(tok.pos_) + 's'
                baseset |= kb.baserefs[toktyp][tok.text.casefold()]
            if not baseset:
                print('No known base types for phrase "{}"'.format(np))
                continue
            for obj in kb.objects.values():
                p = reduce(
                    operator.mul,
                    (max(kb.query_is(t, b) for t in obj.types)
                        for b in baseset))
                print("{} -> (object {!r}): {}".format(np, obj.name, p))

