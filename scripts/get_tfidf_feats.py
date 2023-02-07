#!/usr/bin/env python3

import sys
import joblib
import numpy as np

from tqdm import tqdm

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
    model = joblib.load('en-de.tfidf.joblib')
    feature_array = np.array(model.get_feature_names_out())

    for docs in grouper(map(str.strip, sys.stdin), 2*1024):
        feats = get_feats(docs, model, feature_array)
        for feat in feats:
            print(" ".join(feat))
