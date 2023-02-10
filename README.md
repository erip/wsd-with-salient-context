# Improving Word Sense Disambiguation in Neural Machine Translation with Salient Document Context


## Environment setup

```bash
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

Then install [`fairseq`](https://github.com/facebookresearch/fairseq). In addition, we use several unix-y features from [here](https://github.com/mjpost/bin). Namely, we need:

- `unpaste`: a sibling to normal unix `paste`
- `rsample`: a stdin/stdout reservoir sampler

## Processing the training data

To download the ParaCrawl data for a given English-X language (where `TGT=X`), create pseudo-documents, and learn noisy TFIDF features from the English side:

```bash
TGT=de bash collect_data.sh
```

Relevant environment variables; can be overriden.

| Variable           | Default             | Purpose                                                                                 |
|--------------------|---------------------|-----------------------------------------------------------------------------------------|
| `$RAW_DATA`          | `$PWD/raw_data`       | Where the TMX and pre-filtered bitext will be stored                                    |
| `$INTERMEDIATE_DATA` | `$PWD/intermediate`   | Where filtered pseudo-documents will be stored                                          |
| `$TOKENIZED_DATA`    | `$PWD/tokenized_data` | Where the post-filtered tokenized pseudo-documents will be stored (for salient context) |

## Extracting salient context from training/validation data

Given the pseudo-documents and the various saliency function extraction logic, we can extract a docid to salient document context mapping with the following:

```bash
TGT=de bash extract_training_context.sh
```

Relevant environment variables; can be overriden.

| Variable           | Default             | Purpose                                                                                 |
|--------------------|---------------------|-----------------------------------------------------------------------------------------|
| `$RAW_DATA`          | `$PWD/raw_data`       | Where the TMX and pre-filtered bitext will be stored                                    |
| `$INTERMEDIATE_DATA` | `$PWD/intermediate`   | Where filtered pseudo-documents will be stored                                          |
| `$TOKENIZED_DATA`    | `$PWD/tokenized_data` | Where the post-filtered tokenized pseudo-documents will be stored (for salient context) |

## Subword encoding and getting ready for fairseq

We can now get everything ready for fairseq. This prepares data for all systems except the shuffled ones.

```bash
TGT=de bash prep_training_data.sh
```

## Fairseq preprocessing

With all the data prepared, we can process the data for a given `$SALIENCY_FUNCTION` (e.g., tfidf5, yake10). This handles the splits for you, but you can change the number of workers by setting `NWORKERS` (20 by default).

```bash
TGT=de SALIENCY_FUNCTION=tfidf5 bash fairseq_preprocess.sh
```

## Training

To train a model with a given `$SALIENCY_FUNCTION` with default hyperparameters:

```bash
SALIENCY_FUNCTION=tfidf5 bash train.sh
```

# Evaluation

Assuming system outputs in `hyps/`, the WSD-specific evaluation can be performed with `bash eval.sh`. We note that some aspects of the resulting table are functions of training data distributions and refer you to `test/README.md` for specifics.