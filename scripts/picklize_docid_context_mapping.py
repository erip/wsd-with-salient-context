#!/usr/bin/env python3

import pickle
from argparse import ArgumentParser, FileType

def setup_argparse():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", type=FileType("r"), default="-")
    parser.add_argument("-o", "--output-file", type=FileType("wb"), required=True)
    return parser

if __name__ == "__main__":
    args = setup_argparse().parse_args()
    d = {}
    with args.input as fin:
        for line in map(lambda s: s.strip("\r\n"), fin):
             id_, context = line.split("\t")
             d[id_] = context

    with args.output_file as out:
        pickle.dump(d, out)
