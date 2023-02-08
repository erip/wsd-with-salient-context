#!/usr/bin/env bash
set -ex

if [ "${SALIENCY_FUNCTION}" = "" ]; then
  echo "SALIENCY_FUNCTION must be set"
fi


DATA_DIR=$(find ${SALIENCY_FUNCTION}-data-bin -maxdepth 2 -mindepth 1 -type d | paste -s -d:)
SAVEDIR="${SALIENCY_FUNCTION}-transformer"
TB_LOGDIR="$SAVEDIR/tb_logs"

mkdir -p "$SAVEDIR"
mkdir -p "$TB_LOGDIR"
SEED=1234
DATE=$(date +'%Y-%m-%d')

fairseq-train $DATA_DIR \
  -a transformer \
  --max-tokens 32768 \
  --update-freq 1 \
  --num-workers 10 \
  --max-epoch 30 \
  --max-source-positions 256 \
  --max-target-positions 256 \
  --keep-last-epochs 5 \
  --memory-efficient-fp16 \
  --save-dir $SAVEDIR \
  --seed $SEED \
  --share-all-embeddings \
  --tensorboard-logdir $TB_LOGDIR \
  --dropout 0.1 \
  --attention-dropout 0.0 \
  --relu-dropout 0.0 \
  --weight-decay 0.0 \
  --optimizer adam --adam-betas '(0.9, 0.98)' \
  --clip-norm 0.0 \
  --skip-invalid-size-inputs-valid-test \
  --criterion label_smoothed_cross_entropy \
  --label-smoothing 0.1 \
  --lr-scheduler inverse_sqrt \
  --warmup-updates 4000 \
  --warmup-init-lr 1e-7 --lr 0.0005 --stop-min-lr 1e-9 \
  --ddp-backend no_c10d \
  --log-format json \
  --fix-batches-to-gpus \
  --log-interval 100 \
  --log-file "$SAVEDIR/log.$DATE"
