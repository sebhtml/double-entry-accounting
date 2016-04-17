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
    def makeVirtualSelfExpenseTransaction(self):
        transaction = copy.copy(self)
        transaction.amount = (1 - self.getModifier()) * self.getAmount()
        transaction.modifier = 1
        transaction.destinationAccount = self.getSourceAccount() + "+expenses+self"
        transaction.sourceAccount = self.getSourceAccount() + "+expenses"
        return transaction
    def makeVirtualNotSelfExpenseTransaction(self):
        transaction = copy.copy(self)
        transaction.amount = self.getModifier() * self.getAmount()
        transaction.modifier = 1
        transaction.destinationAccount = self.getSourceAccount() + "+expenses+not-self"
        transaction.sourceAccount = self.getSourceAccount() + "+expenses"
        return transaction
    def makeVirtualIncomeTransaction(self):
        transaction = copy.copy(self)
        transaction.modifier = 1
        transaction.destinationAccount = self.getDestinationAccount() + "+income"
        transaction.sourceAccount = self.getDestinationAccount() + "+income-source"
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
    def printTransactions(self):
        name = self.getName()
        currency = self.getCurrency()
        balance = self.getBalance()
        print("Account: " + name + "    Balance: " + str(balance)+ "    Currency: " + currency + "    Transactions: " + str(self.getTransactionCount()))

        transactionString = "  %-15s %-20s %-30s %-30s %10s %10s"
        print(transactionString % ("Date", "Description", "DestinationAccount", "SourceAccount", "Amount", "Currency"))

        for transaction in self.getTransactions():
            print(transaction)


        print("")

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

def addTransactions(transactions, factory):
    for transaction in transactions:
        destinationAccountName = transaction.getDestinationAccount()
        sourceAccountName = transaction.getSourceAccount()
        if destinationAccountName == sourceAccountName:
            print("Error: same account")
            continue
        currency = transaction.getCurrency()
        destinationAccount = factory.getAccount(destinationAccountName, currency)
        sourceAccount = factory.getAccount(sourceAccountName, currency)
        destinationAccount.addTransaction(transaction)
        sourceAccount.addTransaction(transaction)

def main(arguments):
    transactions = []

    transactionFactory = TransactionFactory()
    accountFactory = AccountFactory()
    virtualAccountFactory = AccountFactory()

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

    virtualTransactions = []
    for transaction in transactions:
        virtualSelfTransaction = transaction.makeVirtualSelfExpenseTransaction()
        virtualTransactions.append(virtualSelfTransaction)

        virtualOtherTransaction = transaction.makeVirtualNotSelfExpenseTransaction()
        virtualTransactions.append(virtualOtherTransaction)

        virtualIncomeTransaction = transaction.makeVirtualIncomeTransaction()
        virtualTransactions.append(virtualIncomeTransaction)

        #print("DEBUG " + str(transaction))
        #processTransaction(transaction, virtualTransactions)

    #oldCount = len(transactions)
    #newCount = len(allTransactions)

    #print("oldCount " + str(oldCount) + " newCount: " + str(newCount) + " expected: " + str(3 * oldCount))

    #goodTransactions = 0

    addTransactions(transactions, accountFactory)
    addTransactions(virtualTransactions, virtualAccountFactory)

    print("Account transactions")
    print("")
    for account in accountFactory.getAccounts():
        account.printTransactions()

    print("Virtual account transactions")
    print("")
    for account in accountFactory.getAccounts():
        account.printTransactions()

    print("Account balances")
    #print("")
    print("%-30s %10s %10s" % ("Account", "Amount", "Currency"))

    accounts = accountFactory.getAccounts()
    for account in accounts:
        name = account.getName()
        balance = account.getBalance()
        currency = account.getCurrency()
        print("%-30s %10.2f %10s" % (name, balance, currency))
    print("")

    print("Virtual account balances")
    #print("")
    print("%-30s %10s %10s" % ("Account", "Amount", "Currency"))

    accounts = virtualAccountFactory.getAccounts()
    for account in accounts:
        name = account.getName()
        balance = account.getBalance()
        currency = account.getCurrency()
        print("%-30s %10.2f %10s" % (name, balance, currency))
    print("")

    print("Virtual account balance differences")
    for account1 in accounts:
        for account2 in accounts:
            if account1.getCurrency() == account2.getCurrency():
                name1 = account1.getName()
                name2 = account2.getName()
                currency = account1.getCurrency()
                if name1 == name2:
                    continue
		if not name1.find("+expenses+not-self") >= 0:
                    continue
		if not name2.find("+expenses+not-self") >= 0:
                    continue
                balance1 = account1.getBalance()
                balance2 = account2.getBalance()
                metaBalance = balance1 - balance2
                print("balance(%s) - balance(%s) = %10.2f %10s" % (name1, name2, metaBalance, currency))


main(sys.argv)
