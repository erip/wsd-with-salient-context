#!/usr/bin/env python3

for sys in sent 2sent; do
  SALIENCY_FUNCTION="$sys" bash scripts/eval_system.sh
done

for sf in tfidf yake; do
  for n in 5 10
    for shuf in "" "_shuf"; do
      SALIENCY_FUNCTION="${sf}_${n}${shuf}" bash scripts/eval_system.sh
    done
  done
done
