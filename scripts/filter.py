#!/usr/bin/env python3

from argparse import ArgumentParser, FileType

def setup_argparse():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", type=FileType("r"), default="-")
    parser.add_argument("-o", "--output", type=FileType("w"), default="-")
    parser.add_argment("-m", "--max-sentences", type=int, default=10)
    return parser

if __name__ == "__main__":
    args = setup_argparse().parse_args()

    max_sent = args.max_sentences

    with args.input as fin, args.output as fout:
        for line in map(str.strip, fin):
            id_, src_doc, tgt_doc = line.split("\t")

            assert src_doc.count(" [SENT] ") == tgt_doc.count(" [SENT] ")

            if 2 < src_doc.count(" [SENT] ") < max_sent:
                print(i, src_doc, tgt_doc, sep="\t", file=fout)
