#!/usr/bin/env python

import sys
import os
import copy

class Transaction:
    def __init__(self, line):
        tokens = line.split(',')
        if len(tokens) != 8:
            self.bad = True
            return
        self.date = tokens[0]
        self.description = tokens[1]
        self.destinationAccount = tokens[2]
        self.sourceAccount = tokens[3]
        self.amount = float(tokens[4])
        self.currency = tokens[5]
        self.modifier = float(tokens[6])
        self.approved = int(tokens[7])
        self.bad = False
    def getDate(self):
        return self.date
    def getDestinationAccount(self):
        return self.destinationAccount
    def getSourceAccount(self):
        return self.sourceAccount
    def getCurrency(self):
        return self.currency
    def getAmount(self):
        return self.amount
    def getDescription(self):
        return self.description
    def getModifier(self):
        return self.modifier
    def getApproved(self):
        return self.approved
    def isBad(self):
        return self.bad
    def makeVirtualSelfTransaction(self):
        transaction = copy.copy(self)
        transaction.amount = (1 - self.getModifier()) * self.getAmount()
        transaction.modifier = 1
        transaction.destinationAccount = "virt-" + self.getSourceAccount() + "-destination-self"
        transaction.sourceAccount = "virt-" + self.getSourceAccount() + "-source"
        return transaction
    def makeVirtualOtherTransaction(self):
        transaction = copy.copy(self)
        transaction.amount = self.getModifier() * self.getAmount()
        transaction.modifier = 1
        transaction.destinationAccount = "virt-" + self.getSourceAccount() + "-destination-other"
        transaction.sourceAccount = "virt-" + self.getSourceAccount() + "-source"
        return transaction


class TransactionFactory:
    def __init__(self):
        pass
    def makeTransaction(self, line):
        return Transaction(line)

class Account:
    def __init__(self, name, currency):
        self.name = name
        self.currency = currency
        self.balance = 0
        self.transactions = []
    def addTransaction(self, transaction):
        if transaction.getCurrency() != self.getCurrency():
            print("Error: wrong currency")
            print(transaction)
            return
        if transaction.getDestinationAccount() != self.getName() and transaction.getSourceAccount() != self.getName():
            print("Error: bad account")
            print(transaction)
            return
        if transaction.getDestinationAccount() == transaction.getSourceAccount():
            print("Error: accounts are the same")
            print(transaction)
            return
        amount = transaction.getAmount()
        if transaction.getDestinationAccount() == self.getName():
            self.balance += amount
        elif transaction.getSourceAccount() == self.getName():
            self.balance -= amount
        self.transactions.append(transaction)
    def getCurrency(self):
        return self.currency
    def getBalance(self):
        return self.balance
    def getName(self):
        return self.name
    def getTransactions(self):
        return self.transactions

class AccountFactory:
    def __init__(self):
        self.accounts = {}
    def makeAccount(self, name, currency):
        if name in self.accounts:
            return self.accounts[name]
        account = Account(name, currency)
        self.accounts[name] = account
        return account
    def getAccount(self, name, currency):
        return self.makeAccount(name, currency)
    def getAccounts(self):
        accounts = []
        names = self.accounts.keys()
        names.sort()

        for i in names:
            accounts.append(self.accounts[i])
        return accounts

def processTransaction(transaction, makeVirtualTransaction, accountFactory):
    destinationAccount = transaction.getDestinationAccount()
    sourceAccount = transaction.getSourceAccount()

    currency = transaction.getCurrency()
    if destinationAccount != sourceAccount:
        accountFactory.getAccount(destinationAccount, currency).addTransaction(transaction)
        accountFactory.getAccount(sourceAccount, currency).addTransaction(transaction)

        if not makeVirtualTransaction:
            return

        virtualSelfTransaction = transaction.makeVirtualSelfTransaction()
        processTransaction(virtualSelfTransaction, False, accountFactory)

        virtualOtherTransaction = transaction.makeVirtualOtherTransaction()
        processTransaction(virtualOtherTransaction, False, accountFactory)


def main(arguments):
    transactions = []

    transactionFactory = TransactionFactory()
    accountFactory = AccountFactory()

    for i in arguments:
        if os.path.isfile(i):
            for line in open(i):
                if len(line) > 0:
                    firstCharacter = line[0]
                    if firstCharacter != '#' and len(line.strip()) > 0:
                        transaction = transactionFactory.makeTransaction(line)
                        if transaction.isBad():
                            continue

                        processTransaction(transaction, True, accountFactory)

    print("Transactions")
    print("")
    for account in accountFactory.getAccounts():
        name = account.getName()
        currency = account.getCurrency()
        print("account: " + name + "        currency: " + currency)

        transactionString = "  %-15s %-20s %-30s %-30s %10s %10s"
        print(transactionString % ("Date", "Description", "DestinationAccount", "SourceAccount", "Amount", "Currency"))

        for transaction in account.getTransactions():
            date = transaction.getDate()
            description = transaction.getDescription()
            destinationAccount = transaction.getDestinationAccount()
            sourceAccount = transaction.getSourceAccount()
            amount = transaction.getAmount()

            print("  %-15s %-20s %-30s %-30s %10.2f %10s" % (date, description, destinationAccount, sourceAccount, amount, currency))
        print("")


    print("Balances")
    #print("")
    print("%-30s %10s %10s" % ("Account", "Amount", "Currency"))
    for account in accountFactory.getAccounts():
        name = account.getName()
        balance = account.getBalance()
        currency = account.getCurrency()

        print("%-30s %10.2f %10s" % (name, balance, currency))


main(sys.argv)
