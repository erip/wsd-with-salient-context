#!/usr/bin/env bash

if [[ "$SALIENCY_FUNCTION" = "" ]]; then
  echo "SALIENCY_FUNCTION must be set"
  exit 1
fi

HYP_FILE=hyps/${SALIENCY_FUNCTION}.de

out_file="eval/${SALIENCY_FUNCTION}.lemma"
unk_out_file="eval/${SALIENCY_FUNCTION}.unk"

if [[ ! -f "${out_file}" ]]; then
    cat ${HYP_FILE} | python scripts/write_conllu.py > ${out_file}
fi

python3 scripts/evaluate.py \
  --ref-testsuite test/pseudodocs.en-de.tsv \
  --sense-file test/paracrawl-senses.en-de.txt \
  --dist-file test/distances.en-de.txt \
  --src-segmented test/mucow.sent.en.tok \
  --tgt-segmented <(cat ${HYP_FILE} | sacremoses tokenize) \
  --unk-out $unk_out_file \
  --tgt-lemmatized ${out_file} | column -t > eval/${SALIENCY_FUNCTION}.table
