# Improving Word Sense Disambiguation in Neural Machine Translation with Salient Document Context


## Processing the training data

```bash
TGT=de bash preproc.sh
```

## Extracting salient context from training data

```bash
# Extracts the 10 most highly weighted tfidf features; can re-use for <10 w/ `cut`
python scripts/get_tfidf_feats.py -i ${TOKENIZED_DATA}/bos.en-de.txt | paste ${INTERMEDIATE_DATA}/ids.en-de.txt - > docid_to_tfidf_feats.en-de.tsv

# Extracts the 10 most highly weighted YAKE features; can re-use for <10 w/ `cut`
paste ${INTERMEDIATE_DATA}/ids.en-de.txt ${TOKENIZED_DATA}/bos.en-de.txt | python scripts/get_yake_feats.py > docid_to_yake_feats.en-de.tsv
```
