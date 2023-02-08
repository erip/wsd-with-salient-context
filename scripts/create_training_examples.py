#!/usr/bin/env python3

from argparse import ArgumentParser, FileType

def setup_argparse():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", type=FileType("r"), default="-")
    parser.add_argument("-o", "--output", type=FileType("w"), default="-")
    return parser

if __name__ == "__main__":
    args = setup_argparse().parse_args()
    with args.input as fin, args.output as fout:
        for line in map(str.strip, fin):
            id_, src_doc, tgt_doc = line.split("\t")
            src_sents = src_doc.split(" [SENT] ")
            tgt_sents = tgt_doc.split(" [SENT] ")
            assert len(src_sents) == len(tgt_sents)
            for src_sent, tgt_sent in zip(src_sents, tgt_sents):
                print(id_, src_sent, tgt_sent, sep="\t", file=fout)
