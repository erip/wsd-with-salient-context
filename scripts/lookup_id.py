#!/usr/bin/env python3

import pickle
from argparse import ArgumentParser, FileType

def setup_argparse():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", type=FileType("r"), default="-")
    parser.add_argument("-o", "--output", type=FileType("w"), default="-")
    parser.add_argument("-m", "--model", type=FileType("rb"), required=True)
    return parser

if __name__ == "__main__":
    args = setup_argparse().parse_args()
    d = pickle.load(args.model)
    with args.input as fin, args.output as fout:
        for id_ in map(str.strip, fin):
            print(d[id_], file=fout)
