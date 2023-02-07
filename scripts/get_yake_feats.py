#!/usr/bin/env python3

from argparse import ArgumentParser, FileType
from yake import KeywordExtractor

def setup_argparse():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", type=FileType("r"), default="-")
    parser.add_argument("-o", "--output", type=FileType("w"), default="-")
    return parser

if __name__ == "__main__":
    extractor = KeywordExtractor(lan="en", n=1, top=10)
    args = setup_argparse().parse_args()
    with args.input as fin, args.output as fout:
        for line in map(str.strip, fin):
            id_, text = line.split("\t")
            keywords = extractor.extract_keywords(text.replace(" [SENT] ", "").lower())
            print(id_, " ".join(kw[0] for kw in keywords), sep="\t", file=fout)
