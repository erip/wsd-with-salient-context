#!/usr/bin/env python3

import re
import sys
import random


class FatTrimmer:
    def __init__(self):
        self.res = [
            re.compile(r"\?.*"),
            re.compile(r"^https?://"),
            re.compile(r"^www\."),
        ]

    def __call__(self, text):
        urls = set()
        for url in text.split():
            for regex in self.res:
                url = re.sub(regex, "", text)
            urls.add(url)
        return urls

def trim_urls(data):
    urls = set()
    if isinstance(data, str):
        data = line.split()

    for url in data:
        url = re.sub(r"\?.*", "", url)
        url = re.sub(r"^https?://", "", url)
        url = re.sub(r"^www\.", "", url)

        urls.add(url)

    return urls


def main(args):
    for line in sys.stdin:
        urls = set()
        fields = line.rstrip().split("\t")
        for fieldno in args.fields:
            urls = urls.union(urls, trim_urls(fields[fieldno]))

        num_sources = len(urls)
        if not args.max or len(urls) <= args.max:
            docname = " ".join(sorted(urls))
            print(docname)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--fields", "-f", nargs="+", type=int, default=[-1])
    parser.add_argument("--max", "-m", type=int, default=0)
    args = parser.parse_args()

    main(args)
