# Improving Word Sense Disambiguation in Neural Machine Translation with Salient Document Context


## Processing the training data

```bash
# set RAW_DATA to a place with a lot of disk space :-)
export RAW_DATA="raw_data"
export TOKENIZED_DOCS="tokenized_data"

# Download the TMX
wget https://web-language-models.s3.us-east-1.amazonaws.com/paracrawl/release9/en-de/en-de.tmx.gz -P ${RAW_DATA} 

# Create docid -> pseudo-doc TSV; mapping.en-de.tsv shows the docid to URL set mapping 
python scripts/parse_tmx.py -i ${RAW_DATA}/en-de.tmx.gz -o ${RAW_DATA}/bos.en-de.tsv -m ${RAW_DATA}/mapping.en-de.tsv -s en

# Tokenize each sentence in the pseudo-documents, retaining associated docid
python scripts/tokenize_docs.py -i ${RAW_DATA}/bos.en-de.tsv --max-sentences 10 | unpaste ${TOKENIZED_DOCS}/{ids,bos}.en-de.txt
```
