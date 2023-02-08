#!/usr/bin/env bash
set -ex

if [ "$TGT" = "" ]; then
  echo "TGT must be set"
  exit 2
fi

export RAW_DATA="raw_data"
export INTERMEDIATE_DATA="intermediate"
export TOKENIZED_DATA="tokenized_data"
export TRAINING_DATA="training_data"

seq 0 3 | xargs -I{} mkdir -p ${TRAINING_DATA}/split{}

paste ${INTERMEDIATE_DATA}/{ids,en,${TGT}}.en-${TGT}.txt | python scripts/create_training_examples.py | shuf | unpaste ${TRAINING_DATA}/train.en-${TGT}.{id,en,${TGT}}

num_examples=`wc -l ${TRAINING_DATA}/train.en-${TGT}.id | cut -f1 -d ' '`
quarter_of_lines=$(python -c "print(round(${num_examples}/4)+1)")

paste ${TRAINING_DATA}/train.en-${TGT}.{id,en,${TGT}} | split -d -l ${quarter_of_lines} - ${TRAINING_DATA}/x

seq 0 3 | xargs -I{} bash -c 'cat ${TRAINING_DATA}/x0{} | unpaste ${TRAINING_DATA}/split{}/train.en-${TGT}.{id,en,${TGT}}'
rm ${TRAINING_DATA}/x0{0,1,2,3}
