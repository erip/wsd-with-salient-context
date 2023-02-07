# Improving Word Sense Disambiguation in Neural Machine Translation with Salient Document Context


## Processing the training data

```bash
# set RAW_DATA to a place with a lot of disk space :-)
export RAW_DATA="raw_data"
export INTERMEDIATE_DATA="intermediate"
export TOKENIZED_DATA="tokenized_data"

mkdir -p $RAW_DATA
mkdir -p $INTERMEDIATE_DATA
mkdir -p $TOKENIZED_DATA

# Download the TMX
wget https://web-language-models.s3.us-east-1.amazonaws.com/paracrawl/release9/en-de/en-de.tmx.gz -P ${RAW_DATA} 

# Create docid -> pseudo-doc TSV; mapping.en-de.tsv shows the docid to URL set mapping 
python scripts/parse_tmx.py -i ${RAW_DATA}/en-de.tmx.gz -o ${RAW_DATA}/bos.en-de.tsv -m ${RAW_DATA}/mapping.en-de.tsv -s en

# Filter documents 
python scripts/filter.py -i ${RAW_DATA}/bos.en-de.tsv --max-sentences 10 | unpaste ${INTERMEDIATE_DATA}/{ids,en,de}.en-de.txt

# Tokenize each sentence in the pseudo-documents, retaining associated docid
paste ${INTERMEDIATE_DATA}/en.en-de.txt | python scripts/tokenize_docs.py -o ${TOKENIZED_DATA}/bos.en-de.txt

# Learn tfidf features
cat ${TOKENIZED_DATA}/bos.en-de.txt | rsample --seed 1234 10_000_000 | python scripts/train_tfidf.py -o en-de.tfidf.joblib
```

## Extracting salient context from training data

```bash
# Extracts the 10 most highly weighted tfidf features; can re-use for <10 w/ `cut`
python scripts/get_tfidf_feats.py -i ${TOKENIZED_DATA}/bos.en-de.txt | paste ${INTERMEDIATE_DATA}/ids.en-de.txt - > docid_to_tfidf_feats.en-de.tsv

# Extracts the 10 most highly weighted YAKE features; can re-use for <10 w/ `cut`
paste ${INTERMEDIATE_DATA}/ids.en-de.txt ${TOKENIZED_DATA}/bos.en-de.txt | python scripts/get_yake_feats.py > docid_to_yake_feats.en-de.tsv
```
