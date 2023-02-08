#!/usr/bin/env bash
set -ex

if [ "$TGT" = "" ]; then
  echo "TGT must be set"
  exit 2
fi

export RAW_DATA="${RAW_DATA:=raw_data}"
export INTERMEDIATE_DATA="${INTERMEDIATE_DATA:=intermediate}"
export TOKENIZED_DATA="${TOKENIZED_DATA:=tokenized_data}"
export TRAINING_DATA="${TRAINING_DATA:=training_data}"
export BASELINE_BPE_DATA="${BASELINE_BPE_DATA:=sent_bpe_data}"
export YAKE5_BPE_DATA="${YAKE5_BPE_DATA:=yake5_bpe_data}"
export YAKE10_BPE_DATA="${YAKE10_BPE_DATA:=yake10_bpe_data}"
export TFIDF5_BPE_DATA="${TFIDF5_BPE_DATA:=tfidf5_bpe_data}"
export TFIDF10_BPE_DATA="${TFIDF10_BPE_DATA:=tfidf10_bpe_data}"
export _2SENT_BPE_DATA="${_2SENT_BPE_DATA:=2sent_bpe_data}"

seq 0 3 | xargs -I{} mkdir -p ${TRAINING_DATA}/split{}

function bpe_encode() {
  spm_model=$1
  input_stream=$2
  output_stream=$3
  spm_encode --model $spm_model --input "${input_stream}" --output "${output_stream}"
}

function lookup_context() {
  pkl=$1
  id_stream=$2
  output_stream=$3
  python scripts/lookup_id.py -i $id_stream -o $output_stream -m $pkl
}

function lookup_context_2sent() {
  pkl=$1
  id_stream=$2
  output_stream=$3
  python scripts/lookup_id_2sent.py -i $id_stream -o $output_stream -p $pkl
}

function create_saliency_bpe() {
  TRAINING_DATA=$1
  saliency_function_suffix=$2
  out_dir=$3
  BASELINE_BPE_DATA=$4
  TGT=$5
  for i in 0 1 2 3; do
    bpe_encode model.en-${TGT}.model <(paste "${TRAINING_DATA}/split${i}/train.en-${TGT}".{${saliency_function_suffix},en} | awk -F'\t' '{ print $1 " <SEP> " $2 }') "${out_dir}/split${i}/train.en-${TGT}.bpe.en"
    cp "${BASELINE_BPE_DATA}/split${i}/train.en-${TGT}.bpe.${TGT}" "${out_dir}/split${i}/"
  
    bpe_encode model.en-${TGT}.model <(paste "${TRAINING_DATA}/split${i}/valid.en-${TGT}".{${saliency_function_suffix},en} | awk -F'\t' '{ print $1 " <SEP> " $2 }') "${out_dir}/split${i}/valid.en-${TGT}.bpe.en"
    cp "${BASELINE_BPE_DATA}/split${i}/valid.en-${TGT}.bpe.${TGT}" "${out_dir}/split${i}/"
  
  done 
}


export -f bpe_encode
export -f lookup_context
export -f lookup_context_2sent

# Don't re-split, etc. if the training data is already available
if [ ! -f "${TRAINING_DATA}/split0/train.en-${TGT}.id" ]; then 
  seq 0 3 | xargs -I{} mkdir -p ${TRAINING_DATA}/split{}

  paste ${INTERMEDIATE_DATA}/{ids,en,${TGT}}.en-${TGT}.txt | python scripts/create_training_examples.py | shuf | unpaste ${TRAINING_DATA}/train.en-${TGT}.{id,en,${TGT}}

  num_examples=`wc -l ${TRAINING_DATA}/train.en-${TGT}.id | cut -f1 -d ' '`
  quarter_of_lines=$(python -c "print(round(${num_examples}/4)+1)")

  paste ${TRAINING_DATA}/train.en-${TGT}.{id,en,${TGT}} | split -d -l ${quarter_of_lines} - ${TRAINING_DATA}/x

  seq 0 3 | xargs -I{} bash -c 'cat ${TRAINING_DATA}/x0{} | unpaste ${TRAINING_DATA}/split{}/train.en-${TGT}.{id,en,${TGT}}'
  seq 0 3 | xargs -I{} cp ${RAW_DATA}/valid.en-${TGT}.{id,en,${TGT}} ${TRAINING_DATA}/split{}/
  rm ${TRAINING_DATA}/x0{0,1,2,3}
fi

# get tfidf10 if we need them
test -f ${TRAINING_DATA}/split0/train.en-${TGT}.tfidf10 || (seq 0 3 | xargs -I{} bash -c 'lookup_context train_docid_to_tfidf_feats.en-${TGT}.pkl ${TRAINING_DATA}/split{}/train.en-${TGT}.id ${TRAINING_DATA}/split{}/train.en-${TGT}.tfidf10 ')
test -f ${TRAINING_DATA}/split0/valid.en-${TGT}.tfidf10 || (seq 0 3 | xargs -I{} bash -c 'lookup_context valid_docid_to_tfidf_feats.en-${TGT}.pkl ${RAW_DATA}/valid.en-${TGT}.id ${TRAINING_DATA}/split{}/valid.en-${TGT}.tfidf10 ')

# get tfidf5 if we need them
test -f ${TRAINING_DATA}/split0/train.en-${TGT}.tfidf5 || (seq 0 3 | xargs -I{} bash -c 'cut -d" " -f-5 ${TRAINING_DATA}/split{}/train.en-${TGT}.tfidf10 > ${TRAINING_DATA}/split{}/train.en-${TGT}.tfidf5')
test -f ${TRAINING_DATA}/split0/valid.en-${TGT}.tfidf5 || (seq 0 3 | xargs -I{} bash -c 'cut -d" " -f-5 ${TRAINING_DATA}/split{}/valid.en-${TGT}.tfidf10 > ${TRAINING_DATA}/split{}/valid.en-${TGT}.tfidf5')


# get yake10 if we need them
test -f ${TRAINING_DATA}/split0/train.en-${TGT}.yake10 || (seq 0 3 | xargs -I{} bash -c 'lookup_context train_docid_to_yake_feats.en-${TGT}.pkl ${TRAINING_DATA}/split{}/train.en-${TGT}.id  ${TRAINING_DATA}/split{}/train.en-${TGT}.yake10')
test -f ${TRAINING_DATA}/split0/valid.en-${TGT}.yake10 || (seq 0 3 | xargs -I{} bash -c 'lookup_context valid_docid_to_yake_feats.en-${TGT}.pkl ${RAW_DATA}/valid.en-${TGT}.id  ${TRAINING_DATA}/split{}/valid.en-${TGT}.yake10')

# get yake5 if we need them
test -f ${TRAINING_DATA}/split0/train.en-${TGT}.yake5 || (seq 0 3 | xargs -I{} bash -c 'cut -d" " -f-5 ${TRAINING_DATA}/split{}/train.en-${TGT}.yake10 > ${TRAINING_DATA}/split{}/train.en-${TGT}.yake5')
test -f ${TRAINING_DATA}/split0/valid.en-${TGT}.yake5 || (seq 0 3 | xargs -I{} bash -c 'cut -d" " -f-5 ${TRAINING_DATA}/split{}/valid.en-${TGT}.yake10 > ${TRAINING_DATA}/split{}/valid.en-${TGT}.yake5')

# get 2sent if we need them
test -f ${TRAINING_DATA}/split0/train.en-${TGT}.2sent || (seq 0 3 | xargs -I{} bash -c 'lookup_context_2sent train_docid_to_doc_feats.en-${TGT}.pkl <(paste ${TRAINING_DATA}/split{}/train.en-${TGT}.id ${TRAINING_DATA}/split{}/train.en-${TGT}.en) ${TRAINING_DATA}/split{}/train.en-${TGT}.2sent ')
test -f ${TRAINING_DATA}/split0/valid.en-${TGT}.2sent || (seq 0 3 | xargs -I{} bash -c 'lookup_context_2sent valid_docid_to_doc_feats.en-${TGT}.pkl <(paste ${RAW_DATA}/valid.en-${TGT}.id ${RAW_DATA}/valid.en-${TGT}.en) ${TRAINING_DATA}/split{}/valid.en-${TGT}.2sent ')


test -f model.en-${TGT}.model || spm_train \
  --input=<(cat ${TRAINING_DATA}/train.en-${TGT}.{en,${TGT}}) \
  --model_prefix=model.en-${TGT} \
  --input_sentence_size=10000000 \
  --shuffle_input_sentence=true \
  --vocab_size=32000 \
  --character_coverage=0.995 \
  --split_digits \
  --user_defined_symbols="<SEP>"

# Subword segment everything
seq 0 3 | xargs -I{} mkdir -p ${BASELINE_BPE_DATA}/split{}
seq 0 3 | xargs -I{} mkdir -p ${TFIDF5_BPE_DATA}/split{}
seq 0 3 | xargs -I{} mkdir -p ${TFIDF10_BPE_DATA}/split{}
seq 0 3 | xargs -I{} mkdir -p ${YAKE5_BPE_DATA}/split{}
seq 0 3 | xargs -I{} mkdir -p ${YAKE10_BPE_DATA}/split{}
seq 0 3 | xargs -I{} mkdir -p ${_2SENT_BPE_DATA}/split{}


# baseline
seq 0 3  | xargs -I{} bash -c 'bpe_encode model.en-${TGT}.model "${TRAINING_DATA}/split{}/train.en-${TGT}.en" "${BASELINE_BPE_DATA}/split{}/train.en-${TGT}.bpe.en"'
seq 0 3  | xargs -I{} bash -c 'bpe_encode model.en-${TGT}.model "${TRAINING_DATA}/split{}/valid.en-${TGT}.en" "${BASELINE_BPE_DATA}/split{}/valid.en-${TGT}.bpe.en"'

seq 0 3  | xargs -I{} bash -c 'bpe_encode model.en-${TGT}.model "${TRAINING_DATA}/split{}/train.en-${TGT}.${TGT}" "${BASELINE_BPE_DATA}/split{}/train.en-${TGT}.bpe.${TGT}"'
seq 0 3  | xargs -I{} bash -c 'bpe_encode model.en-${TGT}.model "${TRAINING_DATA}/split{}/valid.en-${TGT}.${TGT}" "${BASELINE_BPE_DATA}/split{}/valid.en-${TGT}.bpe.${TGT}"'

# tfidf5
create_saliency_bpe $TRAINING_DATA "tfidf5" $TFIDF5_BPE_DATA $BASELINE_BPE_DATA $TGT
# tfidf10
create_saliency_bpe $TRAINING_DATA "tfidf10" $TFIDF10_BPE_DATA $BASELINE_BPE_DATA $TGT

# yake5
create_saliency_bpe $TRAINING_DATA "yake5" $YAKE5_BPE_DATA $BASELINE_BPE_DATA $TGT
# yake10
create_saliency_bpe $TRAINING_DATA "yake10" $YAKE10_BPE_DATA $BASELINE_BPE_DATA $TGT

# 2sent
create_saliency_bpe $TRAINING_DATA "2sent" $_2SENT_BPE_DATA $BASELINE_BPE_DATA $TGT