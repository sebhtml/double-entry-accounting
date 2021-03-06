#!/usr/bin/env python

import sys
from finance import *

input = sys.argv[1]

def main():
    convertor = LedgerConvertor()

    for line in open(input):
        line = line.strip()
        if len(line) == 0:
            continue

        if line[0] == "#":
            continue

        transaction = Transaction(line)

        stream = sys.stdout

        if not transaction.isApproved():
            stream.write("; UNAPPROVED\n")

        convertor.write(transaction, stream)


if __name__ == "__main__":
    main()
