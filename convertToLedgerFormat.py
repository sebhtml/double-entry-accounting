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

        if not transaction.isApproved():
            continue

        stream = sys.stdout

        convertor.write(transaction, stream)


if __name__ == "__main__":
    main()
