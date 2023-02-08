#!/usr/bin/env bash
set -ex

if [ "$TGT" = "" ]; then
  echo "TGT must be set"
  exit 2
fi

export RAW_DATA="${RAW_DATA:=raw_data}"
export INTERMEDIATE_DATA="${INTERMEDIATE_DATA:=intermediate}"
export TOKENIZED_DATA="${TOKENIZED_DATA:=tokenized_data}"

mkdir -p $RAW_DATA
mkdir -p $INTERMEDIATE_DATA
mkdir -p $TOKENIZED_DATA

# Download the TMX
wget -nc https://web-language-models.s3.us-east-1.amazonaws.com/paracrawl/release9/en-${TGT}/en-${TGT}.tmx.gz -P ${RAW_DATA}

# may break if TGT doesn't support docid. We only used WMT21 en-de
sacrebleu -t wmt21 -l en-${TGT} --echo docid src ref | unpaste ${RAW_DATA}/valid.en-${TGT}.{id,en,${TGT}}

# Parse TMX and assign sentences a docid; mapping.en-de.tsv shows the docid to URL set mapping
test -f ${RAW_DATA}/skinny-bos.en-${TGT}.tsv || (python scripts/parse_tmx.py -i ${RAW_DATA}/en-${TGT}.tmx.gz -o ${RAW_DATA}/skinny-bos.en-${TGT}.tsv -m ${RAW_DATA}/mapping.en-${TGT}.tsv -s en)

# Group sentences into documents
test -f ${RAW_DATA}/bos.en-${TGT}.tsv || (sort -nk1 ${RAW_DATA}/skinny-bos.en-${TGT}.tsv | python scripts/docs.py > ${RAW_DATA}/bos.en-${TGT}.tsv)
test -f ${RAW_DATA}/valid.bos.en-${TGT}.tsv || (paste ${RAW_DATA}/valid.en-${TGT}.{id,en,${TGT}} | sort -k1 | python scripts/docs.py > ${RAW_DATA}/valid.bos.en-${TGT}.tsv)

# Filter documents
test -f  ${INTERMEDIATE_DATA}/ids.en-${TGT}.txt || (python scripts/filter.py -i ${RAW_DATA}/bos.en-${TGT}.tsv --max-sentences 10 | unpaste ${INTERMEDIATE_DATA}/{ids,en,${TGT}}.en-${TGT}.txt)

# Tokenize each sentence in the pseudo-documents, retaining associated docid
paste ${INTERMEDIATE_DATA}/en.en-${TGT}.txt | python scripts/tokenize_docs.py -o ${TOKENIZED_DATA}/bos.en-${TGT}.txt
cut -f2 ${RAW_DATA}/valid.bos.en-${TGT}.tsv | python scripts/tokenize_docs.py -o ${TOKENIZED_DATA}/valid.bos.en-${TGT}.txt

# Learn tfidf features
cat ${TOKENIZED_DATA}/bos.en-${TGT}.txt | rsample --seed 1234 10_000_000 | python scripts/train_tfidf.py -o en-${TGT}.tfidf.joblib
