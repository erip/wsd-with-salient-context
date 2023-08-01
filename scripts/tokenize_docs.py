#!/usr/bin/env python3

from sacremoses import MosesTokenizer

from argparse import ArgumentParser, FileType

def setup_argparse():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", type=FileType("r"), default="-")
    parser.add_argument("-o", "--output", type=FileType("w"), default="-")
    parser.add_argument("-s", "--src-lang", type=str, default="en")
    return parser

if __name__ == "__main__":
    args = setup_argparse().parse_args()

    tokenizer = MosesTokenizer(lang=args.src_lang)

    with args.input as fin, args.output as fout:
        for src_sent in map(str.strip, fin):
            sents = src_sent.split(" [SENT] ")
            tokenized_sents = [tokenizer.tokenize(sent, return_str=True, escape=False) for sent in sents]
            print(" [SENT] ".join(tokenized_sents), file=fout)
