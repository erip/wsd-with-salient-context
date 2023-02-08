#!/usr/bin/env bash
set -ex

if [ "$TGT" = "" ]; then
  echo "TGT must be set"
  exit 2
fi

export RAW_DATA="raw_data"
export INTERMEDIATE_DATA="intermediate"
export TOKENIZED_DATA="tokenized_data"

# Extracts the 10 most highly weighted tfidf features; can re-use for <10 w/ `cut`
python scripts/get_tfidf_feats.py -i ${TOKENIZED_DATA}/bos.en-${TGT}.txt -t en-${TGT}.tfidf.joblib | paste ${INTERMEDIATE_DATA}/ids.en-${TGT}.txt - > docid_to_tfidf_feats.en-${TGT}.tsv

# Extracts the 10 most highly weighted YAKE features; can re-use for <10 w/ `cut`
paste ${INTERMEDIATE_DATA}/ids.en-${TGT}.txt ${TOKENIZED_DATA}/bos.en-${TGT}.txt | python scripts/get_yake_feats.py > docid_to_yake_feats.en-${TGT}.tsv
