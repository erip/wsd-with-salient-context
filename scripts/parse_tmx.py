#!/usr/bin/env python3

import csv
import sys
import gzip
import hashlib
import argparse

from trim_fat import trim_urls

from lxml import etree as ET

from collections import Counter

def hash(s):
    return hashlib.sha1(s).hexdigest()

def smart_open(filepath, mode="rt"):
    """
    Generalized open; works for plain files, compressed files, and STDIN.
    """
    infile = None
    if filepath == "-":
        infile = sys.stdin.buffer
    elif filepath.endswith(".gz"):
        infile = gzip.open(filepath, mode)
    else:
        infile = open(filepath, mode)
    return infile


def setup_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("--mapping", "-m", type=argparse.FileType("w"), default=None)
    parser.add_argument("-o", "--output", type=argparse.FileType("w"), default="-", required=True)
    parser.add_argument("-s", "--src", required=True)
    return parser


if __name__ == "__main__":
    args = setup_argparse().parse_args()
    context = ET.iterparse(smart_open(args.input, mode="rb"), tag=("tu",))
    with args.output as f:
        fieldnames = ("docid", "src", "tgt")
        docids = {}

        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for _, elem in context:
            row = {}
            urls = set()
            for tuv in elem.iterfind("tuv"):
                if tuv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == args.src:
                    urls = urls.union(urls, set(e.text.strip() for e in tuv.iterfind("prop") if e is not None and e.attrib.get("type") == "source-document"))
                    row["src"] = tuv.find("seg").text.strip()
                else:
                    urls = urls.union(urls, set(e.text.strip() for e in tuv.iterfind("prop") if e is not None and e.attrib.get("type") == "source-document"))
                    row["tgt"] = tuv.find("seg").text.strip()
            assert not any(e is None for e in row.values()), str(row)

            docname = hash(" ".join(sorted(trim_urls(urls))).encode())
            if not docname in docids:
                print(docname, file=args.mapping)
                docids[docname] = len(docids)
            row["docid"] = docids[docname]

            writer.writerow(row)
            elem.clear()
            for ancestor in elem.xpath("ancestor-or-self::*"):
                while ancestor.getprevious() is not None:
                    del ancestor.getparent()[0]
