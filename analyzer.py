#!/usr/bin/env python

import sys
import os
import copy
import datetime

from finance import *

def main(arguments):
    transactions = []

    transactionFactory = TransactionFactory()
    accountFactory = AccountFactory()

    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")

    for i in arguments:
        if os.path.isfile(i):
            for line in open(i):
                if len(line) > 0:
                    firstCharacter = line[0]
                    if firstCharacter != '#' and len(line.strip()) > 0:
                        transaction = transactionFactory.makeTransaction(line)
                        if transaction.isBad() or not transaction.isApproved():
                            continue
                        if not transaction.getDate() <= today:
                            continue
                        transactions.append(transaction)

    transactions = sorted(transactions, key=lambda transaction: transaction.getDate())

    addTransactions(transactions, accountFactory)

    accounts = accountFactory.getAccounts()
    print("Accounts")
    print("")
    for account in accounts:
        account.printAccount()

    print("Differences")
    for account1 in accounts:
        for account2 in accounts:
            if account1.getCurrency() != account2.getCurrency():
                continue
            name1 = account1.getName()
            name2 = account2.getName()
            currency = account1.getCurrency()
            if name1 == name2:
                continue
            balance1 = account1.getExpensesForAccount(name2)
            balance2 = account2.getExpensesForAccount(name1)
            metaBalance = balance1 - balance2

            if metaBalance < 0:
                continue
            if metaBalance == 0.00:
                continue
            print("balance(%s) - balance(%s) = %10.2f %10s" % (name1, name2, metaBalance, currency))

main(sys.argv)
