#!/usr/bin/env python3

from sacremoses import MosesTokeinzer

from argparse import ArgumentParser, FileType

def setup_argparse():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", type=FileType("r"), default="-")
    parser.add_argument("-o", "--output", type=FileType("w"), default="-")
    parser.add_argument("-m", "--max-sentences", type=int, default=10)
    parser.add_argument("-s", "--src-lang", type=str, default="en")
    return parser

if __name__ == "__main__":
    args = setup_argparse().parse_args()

    tokenizer = MosesTokenizer(lang=args.src_lang)

    with args.input as fin, args.output as fout:
        for line in map(str.strip, fin):
            id_, src_sent, *_ = line.split("\t")
            sents = src_sent.split(" [SENT] ")
            if len(sents) < args.max_sentences:
                tokenized_sents = [tokenizer.tokenize(sent, return_str=True) for sent in sents]
                print(id_, " [SENT] ".join(tokenized_sents), sep="\t", file=fout)
