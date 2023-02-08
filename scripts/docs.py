import sys
import gzip

from typing import Iterable, List, Tuple


def read_docs(infile, docfield=-1) -> Iterable[List[Tuple]]:
    """Generator over documents; returns documents as list of lines.

    :param infile: The file stream to read from.
    :param docfield: The field containing the document ID (default: last field).
    :return: A generator of documents, each a list of tuples. The tuples are the fields (e.g., source, target, docid).
    """
    doc = []
    prev_docid = None
    for lineno, line in enumerate(infile, 1):
        # Split on tabs, then strip whitespace from either side
        fields = list(map(str.strip, line.rstrip().split("\t")))

        docid = fields[docfield] if len(fields) > docfield else None

        if docid != prev_docid or docid is None:
            if len(doc):
                yield doc
            doc = []

        doc.append(tuple(fields))
        prev_docid = docid

    if len(doc):
        yield doc


def smart_open(filepath):
    """
    Generalized open; works for plain files, compressed files, and STDIN.
    """
    infile = None
    if filepath == "-":
        infile = sys.stdin
    elif filepath.endswith(".gz"):
        infile = gzip.open(filepath, "rt")
    else:
        infile = open(filepath, "rt")
    return infile


if __name__ == "__main__":
    f = smart_open('-')
    for d in read_docs(f, 0):
         ids, src, tgt = zip(*d)
         if len(ids) > 1:
             print(ids[0], " [SENT] ".join(src), " [SENT] ".join(tgt), sep="\t")
