#!/usr/bin/env python

import sys
import os
import copy
import datetime

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
    def isApproved(self):
        return self.approved
    def __str__(self):
        date = "" + self.getDate() + ""
        description = self.getDescription()
        destinationAccount = self.getDestinationAccount()
        sourceAccount = self.getSourceAccount()
        amount = self.getAmount()
        currency = self.getCurrency()
        output = "  %-15s %-20s %-30s %-30s %10.2f %10s" % (date, description, destinationAccount, sourceAccount, amount, currency)
        return output
    def isBad(self):
        return self.bad
    def makeVirtualSelfTransaction(self):
        prefix = "virtual:"
        transaction = copy.copy(self)
        transaction.amount = (1 - self.getModifier()) * self.getAmount()
        transaction.modifier = 1
        transaction.destinationAccount = prefix + self.getSourceAccount() + ":self"
        transaction.sourceAccount = prefix + self.getSourceAccount() + ""
        return transaction
    def makeVirtualOtherTransaction(self):
        prefix = "virtual:"
        transaction = copy.copy(self)
        transaction.amount = self.getModifier() * self.getAmount()
        transaction.modifier = 1
        transaction.destinationAccount = prefix + self.getSourceAccount() + ":other"
        transaction.sourceAccount = prefix + self.getSourceAccount() + ""
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
    def getTransactionCount(self):
        return len(self.getTransactions())
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

def processTransaction(transaction, transactions):
    destinationAccount = transaction.getDestinationAccount()
    sourceAccount = transaction.getSourceAccount()

    #currency = transaction.getCurrency()

    if destinationAccount == sourceAccount:
        print("Error: same account")
        return

    transactions.append(transaction)

    #if not makeVirtualTransactions:
        #return

    virtualSelfTransaction = transaction.makeVirtualSelfTransaction()

    virtualOtherTransaction = transaction.makeVirtualOtherTransaction()

    transactions.append(virtualSelfTransaction)
    transactions.append(virtualOtherTransaction)


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

    allTransactions = []
    for transaction in transactions:
        #print("DEBUG " + str(transaction))
        processTransaction(transaction, allTransactions)

    oldCount = len(transactions)
    newCount = len(allTransactions)

    #print("oldCount " + str(oldCount) + " newCount: " + str(newCount) + " expected: " + str(3 * oldCount))

    goodTransactions = 0
    for transaction in allTransactions:
        destinationAccountName = transaction.getDestinationAccount()
        sourceAccountName = transaction.getSourceAccount()
        if destinationAccountName == sourceAccountName:
            print("Error: same account")
            continue
        currency = transaction.getCurrency()
        destinationAccount = accountFactory.getAccount(destinationAccountName, currency)
        sourceAccount = accountFactory.getAccount(sourceAccountName, currency)
        destinationAccountBefore = destinationAccount.getTransactionCount()
        sourceAccountBefore = sourceAccount.getTransactionCount()
        destinationAccount.addTransaction(transaction)
        sourceAccount.addTransaction(transaction)
        destinationAccountAfter = destinationAccount.getTransactionCount()
        sourceAccountAfter = sourceAccount.getTransactionCount()
        if destinationAccountAfter != destinationAccountBefore + 1:
            print("BUG: " + transaction)
        #print("before " + str(destinationAccountBefore) + " after " + str(destinationAccountAfter))
        if sourceAccountAfter != sourceAccountBefore + 1:
            print("BUG: " + transaction)

        goodTransactions += 1

    #print("DEBUG goodTransactions: " + str(goodTransactions))

    print("Transactions")
    print("")
    for account in accountFactory.getAccounts():
        name = account.getName()
        currency = account.getCurrency()
        print("Account: " + name + "        Currency: " + currency + "     Transactions: " + str(len(account.getTransactions())))

        transactionString = "  %-15s %-20s %-30s %-30s %10s %10s"
        print(transactionString % ("Date", "Description", "DestinationAccount", "SourceAccount", "Amount", "Currency"))

        for transaction in account.getTransactions():
            print(transaction)
        print("")


    print("Balances")
    #print("")
    print("%-30s %10s %10s" % ("Account", "Amount", "Currency"))

    accounts = accountFactory.getAccounts()
    for account in accounts:
        name = account.getName()
        balance = account.getBalance()
        currency = account.getCurrency()

        print("%-30s %10.2f %10s" % (name, balance, currency))
    print("")
    print("Virtual balances")
    for account1 in accounts:
        for account2 in accounts:
            if account1.getCurrency() == account2.getCurrency():
                name1 = account1.getName()
                name2 = account2.getName()
                currency = account1.getCurrency()
                if name1 == name2:
                    continue
		if not name1.find("virtual:") >= 0:
                    continue
		if not name1.find(":other") >= 0:
                    continue
		if not name2.find("virtual:") >= 0:
                    continue
		if not name2.find(":other") >= 0:
                    continue
                balance1 = account1.getBalance()
                balance2 = account2.getBalance()
                metaBalance = balance1 - balance2
                print("balance(%s) - balance(%s) = %10.2f %10s" % (name1, name2, metaBalance, currency))


main(sys.argv)
