#!/usr/bin/env python3

import pickle
import random
from argparse import ArgumentParser, FileType

def setup_argparse():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", type=FileType("r"), default="-")
    parser.add_argument("-o", "--output", type=FileType("w"), default="-")
    parser.add_argument("-p", "--pickle", type=FileType("rb"), required=True)
    return parser

if __name__ == "__main__":
    args = setup_argparse().parse_args()

    d = pickle.load(args.pickle)
    with args.input as fin, args.output as fout:
        for line in map(lambda s: s.strip("\r\n"), fin):
            id_, sent = line.split("\t")
            sents = set(d[id_].split(" [SENT] "))
            options = list(sents - {sent})
            context = random.choice(options)
            print(context, file=fout)
