# Improving Word Sense Disambiguation in Neural Machine Translation with Salient Document Context


## Environment setup

```bash
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

In addition, we use several unix-y features from [here](https://github.com/mjpost/bin). Namely, we need:

- `unpaste`: a sibling to normal unix `paste`
- `rsample`: a stdin/stdout reservoir sampler

## Processing the training data

To download the ParaCrawl data for a given English-X language (where `TGT=X`), create pseudo-documents, and learn noisy TFIDF features from the English side:

```bash
TGT=de bash preproc.sh
```

## Extracting salient context from training data

Given the pseudo-documents and the various saliency function extraction logic, we can extract a docid to salient document context mapping with the following:

```bash
TGT=de bash extract_training_context.sh
```
