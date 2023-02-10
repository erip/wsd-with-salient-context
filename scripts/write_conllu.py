#!/usr/bin/env python3

from spacy_conll import init_parser

from argparse import ArgumentParser, FileType

def setup_argparse():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", type=FileType("r"), default="-")
    parser.add_argument("-o", "--output", type=FileType("w"), default="-")
    return parser

if __name__ == "__main__":
    nlp = init_parser("de_core_news_lg", "spacy")
    args = setup_argparse().parse_args()
    lines = [line.strip() for line in args.input]
    batched_docs = nlp.pipe(lines, batch_size=512)
    i = 1
    with args.output as fout:
        for doc in batched_docs:
            print(f"# sent_id = {i}", file=fout)
            print(f"# text = {doc.text}", file=fout)
            print(doc._.conll_str.replace("\n\n", "\n"), file=fout)
            i += 1
