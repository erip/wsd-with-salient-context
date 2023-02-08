#!/usr/bin/env python3

import sys
import joblib
import numpy as np

from tqdm import tqdm

from argparse import ArgumentParser, FileType

def setup_argparse():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", type=FileType("r"), default="-")
    parser.add_argument("-o", "--output", type=FileType("w"), default="-")
    parser.add_argument("-t", "--tfidf-model", type=str, required=True)
    parser.add_argument("-b", "--buffer-size", type=int, default=2048, help="The number of featurize at once.")
    return parser


def get_feats(docs, model, feature_array, n=10):
    docs = [" ".join(doc.split(" [SENT] ")).lower() for doc in docs]

    response = model.transform(docs).toarray()
    response = np.where(response < 1e-4, float('-inf'), response)
    tfidf_sorting = np.argsort(response)
    top_n = feature_array[tfidf_sorting][:, -n:]
    return top_n[:, ::-1]

def grouper(iterable, n):
    iterable = iter(iterable)
    count = 0
    group = []
    while True:
        try:
            group.append(next(iterable))
            count += 1
            if count % n == 0:
                yield group
                group = []
        except StopIteration:
            yield group
            break

if __name__ == "__main__":
    args = setup_argparse().parse_args()
    model = joblib.load(args.tfidf_model)
    feature_array = np.array(model.get_feature_names_out())

    with args.input as fin, args.output as fout:
        for docs in grouper(map(str.strip, fin), args.buffer_size):
            feats = get_feats(docs, model, feature_array)
            for feat in feats:
                print(" ".join(feat), file=fout)
