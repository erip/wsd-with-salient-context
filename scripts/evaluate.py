#! /usr/bin/env python3

import argparse, gzip, collections, itertools, re, html, json


def ConllIterator(f):
	tokensequence, lemmasequence = [], []
	for line in f:
		if line.startswith("#"):
			continue
		elif line.isspace():
			if lemmasequence != []:
				yield tokensequence, lemmasequence
			tokensequence, lemmasequence = [], []
		else:
			data = line.split("\t")
			if '-' in data[0] or '.' in data[0]:
				continue
			tokensequence.append(data[1].lower())
			lemmasequence.append(data[2].lower())
	if lemmasequence != []:
		yield tokensequence, lemmasequence


def loadSenses(sense_file):
	sensecategories = collections.defaultdict(set)
	senses = collections.defaultdict(dict)
	for row in sense_file:
		elements = row.strip().split("\t")
		word = elements[0]
		sense = int(elements[1])
		relfreq = float(elements[3])
		targets = set(elements[4].split(" "))
		senses[word][sense] = targets
		if relfreq < 0.2:
			sensecategories[word, sense].add("freq:0-20")
		elif relfreq < 0.4:
			sensecategories[word, sense].add("freq:20-40")
		elif relfreq < 0.6:
			sensecategories[word, sense].add("freq:40-60")
		elif relfreq < 0.8:
			sensecategories[word, sense].add("freq:60-80")
		else:
			sensecategories[word, sense].add("freq:80-100")
		if (relfreq >= 0.45) and (relfreq < 0.55):
			sensecategories[word, sense].add("freq:45-55")
	return senses, sensecategories


def loadDistances(dist_file):
	distances = collections.defaultdict(dict)
	for row in dist_file:
		elements = row.strip().split("\t")
		word = elements[0]
		sensepair = tuple([int(x) for x in elements[1].split("-")])
		value = float(elements[2])
		distances[word][sensepair] = value
	return distances


def checkSrcSegm(srcword, srcsegmsent):
	if bool(re.search(r'(^|\s)' + re.escape(srcword) + r'(\s|$)', srcsegmsent)):
		return ["srcsplit:no"]
	else:
		return ["srcsplit:yes"]


def checkTgtSegm(sys_token_sent, sys_lemma_sent, sys_segm_sent, all_lemmas):
	for token, lemma in zip(sys_token_sent, sys_lemma_sent):
		# if the lemmatized output contains a matching lemma
		if lemma.lower() in all_lemmas:
			# check if the corresponding inflected form (token) occurs without 
segmentation in bpe_sent
			if bool(re.search(r'(^|\s)' + re.escape(token) + r'(\s|$)', 
sys_segm_sent)):
				return ["tgtsplit:no"]
			else:
				return ["tgtsplit:yes"]
	return []	# don't add any feature if we can't identify the token


def checkDist(ambiglemma, correct_sense, distance_dict, distance_bins):
	wordDistances = [distance_dict[x] for x in distance_dict if correct_sense in x]
	avgWordDistance = sum(wordDistances)/len(wordDistances)
	for name, upperLimit in distance_bins:
		if avgWordDistance < upperLimit:
			return [name]
	return []


def compare(ref_file, src_segm_file, sys_segm_file, sys_lemma_file, senses, sensecategories, 
distances, out_file):
	counts = collections.defaultdict(int)
	lines = collections.defaultdict(int)
	distance_values = [v for x in distances for v in distances[x].values()]
	mindist, maxdist, avgdist = min(distance_values), max(distance_values), 
sum(distance_values)/len(distance_values)
	bins_dist = [("dist:below_avg", avgdist), ("dist:above_avg", maxdist+0.1)]
	
	for ref_sent, src_segm_sent, sys_segm_sent, sys_token_lemma_sent in 
itertools.zip_longest(ref_file, src_segm_file, sys_segm_file, ConllIterator(sys_lemma_file), 
fillvalue=None):
		if not any((ref_sent, src_segm_sent, sys_segm_sent, sys_token_lemma_sent)):
			continue
		lines["total"] += 1
		if ref_sent is None:			
			lines["missing_ref"] += 1
			continue
		if src_segm_sent is None:
			lines["missing_src_segm"] += 1
			continue
		if sys_token_lemma_sent is None:
			lines["missing_sys_lemma"] += 1
			continue
		if sys_segm_sent is None:
			lines["missing_sys_segm"] += 1
			continue
		
		# ref_sent items
		ref_elements = ref_sent.strip().split("\t")
		srcsentence = ref_elements[3].split(" ")
		ambiglemma = ref_elements[0]
		ambigword = ref_elements[5].lower()
		correct_sense = int(ref_elements[1])
		corpus = ref_elements[2]
		all_lemmas = set(itertools.chain.from_iterable(senses[ambiglemma].values()))
		correct_lemmas = senses[ambiglemma][correct_sense]
		incorrect_lemmas = all_lemmas - correct_lemmas
		
		src_segm_sent = html.unescape(src_segm_sent.strip()).lower()
		sys_segm_sent = html.unescape(sys_segm_sent.strip()).lower()
		sys_token_sent, sys_lemma_sent = sys_token_lemma_sent
		
		if ambigword not in distances:
			continue
		
		# determine features to evaluate
		features = ["all"]
		features.append("corp:"+corpus)
		if corpus in ("books", "europarl", "globalvoices", "jw", "tatoeba", "ted"):
			features.append("datasrc:clean")
		else:
			features.append("datasrc:noisy")
		features.extend(sensecategories[ambiglemma, correct_sense])
		features.extend(checkSrcSegm(ambigword, src_segm_sent))
		features.extend(checkTgtSegm(sys_token_sent, sys_lemma_sent, sys_segm_sent, 
all_lemmas))
		features.extend(checkDist(ambiglemma, correct_sense, distances[ambiglemma], 
bins_dist))
		
		if "freq:0-20" in features:
			c = [x for x in features if x.startswith("datasrc:")][0]
			features.append(c + ":0-20")
		
		# check if found
		pos_lemmas = list(set(sys_lemma_sent) & correct_lemmas)
		neg_lemmas = list(set(sys_lemma_sent) & incorrect_lemmas)
		posfound = (len(pos_lemmas) > 0)
		negfound = (len(neg_lemmas) > 0)
		
		for feature in features:
			if posfound and not negfound:
				sense = [x for x in senses[ambiglemma] if pos_lemmas[0] in 
senses[ambiglemma][x]][0]
				counts[feature, "pos"] += 1
				counts[feature, "wpos"] += 1 # maximal similarity
			elif negfound:
				counts[feature, "neg"] += 1
				sense = [x for x in senses[ambiglemma] if neg_lemmas[0] in 
senses[ambiglemma][x]][0]
				sensepair = tuple(sorted([correct_sense, sense]))
				counts[feature, "wpos"] += 1 - distances[ambiglemma][sensepair]		
# similarity between 0 and 1
			else:
				sense = ""
				counts[feature, "unk"] += 1

			if posfound or negfound:
				if sense != correct_sense:
					sensepair = tuple(sorted([correct_sense, sense]))
					counts[feature, "dist_sum"] += 
distances[ambiglemma][sensepair]
				counts[feature, "dist_count"] += 1

		if sense == "":
			contains_any_correct_lemma_substring = any(correct_lemma in 
sys_segm_sent for correct_lemma in correct_lemmas)
			contains_any_incorrect_lemma_substring = any(incorrect_lemma in 
sys_segm_sent for incorrect_lemma in incorrect_lemmas)
			print(json.dumps({"ambig_lemma": ambiglemma, "ref_sent": 
ref_elements[4], "src_segm_sent": src_segm_sent, "sys_segm_sent": sys_segm_sent, 
"correct_lemmas": list(correct_lemmas), "contains_any_correct_lemma_substring": 
contains_any_correct_lemma_substring, "contains_any_incorrect_lemma_substring": 
contains_any_incorrect_lemma_substring}), file=out_file)


	if lines["missing_ref"] + lines["missing_src_segm"] + lines["missing_sys_lemma"] + 
lines["missing_sys_segm"] > 0:
		print("Number of sentences does not match")
		print("Reference file:", lines["total"] - lines["missing_ref"])
		print("Segmented source file:", lines["total"] - lines["missing_sys_bpe"])
		print("Lemmatized system output:", lines["total"] - lines["missing_sys_lemma"])
		print("Segmented system output:", lines["total"] - lines["missing_sys_bpe"])
		print()
		return
	
	features = sorted(set([x[0] for x in counts.keys()]))
	for c in features:
		# Precision = pos / (pos+neg)
		counts[c, "prec"] = 0 if counts[c, "pos"] == 0 else counts[c, "pos"] / 
(counts[c, "pos"] + counts[c, "neg"])
		counts[c, 'wprec'] = 0 if counts[c, 'wpos'] == 0 else counts[c, 'wpos'] / 
(counts[c, 'pos'] + counts[c, 'neg'])
		
		# RecallA = pos / (pos+unk)
		# This is the definition of recall that was used to compute the results tables
		# in the papers, but *does not* correspond to the definition given in the 
papers.
		counts[c, "recA"] = 0 if counts[c, "pos"] == 0 or (c, "unk") not in counts else 
counts[c, "pos"] / (counts[c, "pos"] + counts[c, "unk"])
		counts[c, "f1A"] = 0 if (counts[c, "prec"] + counts[c, "recA"]) == 0 else 2 * 
counts[c, "prec"] * counts[c, "recA"] / (counts[c, "prec"] + counts[c, "recA"])
		counts[c, "wf1A"] = 0 if (counts[c, "wprec"] + counts[c, "recA"]) == 0 else 2 * 
counts[c, "wprec"] * counts[c, "recA"] / (counts[c, "wprec"] + counts[c, "recA"])
		
		# RecallB = pos / (pos+unk+neg)
		# This formula corresponds to the definition given in the papers,
		# but is *not* the one that was used to compute the results tables.
		counts[c, "recB"] = 0 if counts[c, "pos"] == 0 or (c, "unk") not in counts else 
counts[c, "pos"] / (counts[c, "pos"] + counts[c, "unk"] + counts[c, "neg"])
		counts[c, "f1B"] = 0 if (counts[c, "prec"] + counts[c, "recB"]) == 0 else 2 * 
counts[c, "prec"] * counts[c, "recB"] / (counts[c, "prec"] + counts[c, "recB"])
		counts[c, "wf1B"] = 0 if (counts[c, "wprec"] + counts[c, "recB"]) == 0 else 2 * 
counts[c, "wprec"] * counts[c, "recB"] / (counts[c, "wprec"] + counts[c, "recB"])
	
	print("Evaluated file:", sys_lemma_file.name)
	print()
	print("Category", "Pos", "WPos", "Neg", "Unk", "Total", "AvgDist", "Precision", 
"WPrec","RecallA", "F1-ScoreA", "WF1A", "RecallB", "F1-ScoreB", "WF1B", sep="\t")
	for c in features:
		print(c, counts[c, 'pos'], "{:.1f}".format(counts[c, 'wpos']),
			counts[c, 'neg'], counts[c, 'unk'],
			counts[c, "pos"]+counts[c, "neg"]+counts[c, "unk"],
			"{:.4f}".format(counts[c, "dist_sum"] / counts[c, "dist_count"]),
			"{:.4f}".format(counts[c, "prec"]), "{:.4f}".format(counts[c, 
"wprec"]), 
			"{:.4f}".format(counts[c, "recA"]), "{:.4f}".format(counts[c, "f1A"]),
			"{:.4f}".format(counts[c, "wf1A"]),
			"{:.4f}".format(counts[c, "recB"]), "{:.4f}".format(counts[c, "f1B"]),
			"{:.4f}".format(counts[c, "wf1B"]), sep="\t")
	print()
	
	
def anyfile(s):
	try:
		if s.endswith(".gz"):
			f = gzip.open(s, 'rt', encoding='utf-8')
		else:
			f = open(s, 'r', encoding='utf-8')
	except IOError:
		raise argparse.ArgumentError('Cannot open file {}'.format(s))
	return f


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Evaluate MuCoW test suite results')
	parser.add_argument('--src-segmented', type=argparse.FileType('r'), help='the segmented 
input file, one sentence per line')
	parser.add_argument('--tgt-segmented', type=argparse.FileType('r'), help='the segmented 
system output, one sentence per line')
	parser.add_argument('--tgt-lemmatized', type=argparse.FileType('r'), help='the 
de-segmented, lemmatized system output, in CoNLL format')
	parser.add_argument('--ref-testsuite', type=anyfile, help='the test file as defined by 
the test suite')
	parser.add_argument('--unk-out', type=argparse.FileType('w'), default='/dev/null', 
help='The path to which to write unknown examples')
	parser.add_argument('--sense-file', type=argparse.FileType('r'), help='the sense 
definition file')
	parser.add_argument('--dist-file', type=argparse.FileType('r'), help='the file defining 
the distances between senses')
	args = parser.parse_args()
	
	senses, sensecategories = loadSenses(args.sense_file)
	distances = loadDistances(args.dist_file)
	with args.unk_out as out:
		compare(args.ref_testsuite, args.src_segmented, args.tgt_segmented, 
args.tgt_lemmatized, senses, sensecategories, distances, out)
