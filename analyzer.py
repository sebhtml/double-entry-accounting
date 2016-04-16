#!/usr/bin/env python

import sys
import os

class Transaction:
    def init(self, line):
        tokens = line.split ','
        self.date = tokens[0]
        self.description = tokens[1]
        self.destinationAccount = tokens[2]
        self.sourceAccount = tokens[3]
        self.amount = float(tokens[4])
        self.currency = tokens[5]
        self.modifier = float(tokens[6])
        self.approved = int(tokens[7])
    def getDestinationAccount(self):
        return self.destinationAccount
    def getSourceAccount(self):
        return self.sourceAccount
    def getCurrency(self):
        return self.currency
    def getAmount(self):
        return self.amount
    def getModifier(self):
        return self.modifier
    def getApproved(self):
        return self.approved

class TransactionFactory:
    singleton = TransactionFactory()
    def init(self):
        pass
    @staticmethod
    def getSingleton():
        return singleton
    def makeTransaction(self, line):
        return Transaction(line)

class Account:
    def init(self, name, currency):
        self.name = name
        self.currency = currency
        self.balance = 0
        self.transactions = []
    def addTransaction(self, transaction):
        if transaction.getCurrency() != getCurrency():
            print("Error: wrong currency")
            print(transaction)
            return
        if transaction.getDestinationAccount() != getAccount() and transaction.getSourceAccount() != getName():
            print("Error: bad account")
            print(transaction)
            return
        if transaction.getDestinationAccount() == transaction.getSourceAccount():
            print("Error: accounts are the same")
            print(transaction)
            return
        self.transactions.append(transaction)

        amount = transaction.getAmount()

        if transaction.getDestinationAccount() == getAccount():
            self.balance += amount
        elif transaction.getSourceAccount() == getAccount():
            self.balance -= amount
    def getCurrency(self):
        return self.currency
    def getBalance(self):
        return self.balance
    def getName(self):
        return self.name

def main(arguments):
    transactions = []

    for i in arguments:
        if os.path.isfile(i):
            for line in open(i):
                if len(line) > 0:
                    if line[0]  != '#':
                        transaction = TransactionFactory.getSingleton().makeTransaction(line)





main(sys.argv)
