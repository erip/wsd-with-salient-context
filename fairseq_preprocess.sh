#!/usr/bin/env bash

if [ "$SALIENCY_FUNCTION" = "" ]; then
  echo "SALIENCY_FUCNTION must be set"
  exit 2
fi

if [ "$TGT" = "" ]; then
  echo "TGT must be set"
  exit 2
fi


NWORKERS=${NWORKERS:=20}

mkdir -p ${SALIENCY_FUNCTION}-data-bin

for i in 0 1 2 3; do
  mkdir -p ${SALIENCY_FUNCTION}-data-bin/data-bin-$i
  fairseq-preprocess -s en -t ${TGT} \
    --trainpref ${SALIENCY_FUNCTION}_bpe_data/split$i/train.en-${TGT}.bpe \
    --validpref ${SALIENCY_FUNCTION}_bpe_data/split$i/valid.en-${TGT}.bpe \
    --joined-dictionary --workers $NWORKERS \
    --srcdict <(tail -n+4 model.en-${TGT}.vocab | awk '{ print $1 " 100" }') \
    --destdir ${SALIENCY_FUNCTION}-data-bin/data-bin-$i
done
