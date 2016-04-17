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
        self.modifiers = []

        selfModifier = 1.0
        modifierTokens = tokens[6].split()
        i = 0
        while i < len(modifierTokens):
            account = modifierTokens[i]
            modifier = float(modifierTokens[i + 1])
            if account != self.getSourceAccount():
                self.modifiers.append([account, modifier])
                selfModifier -= modifier
            i += 2

        self.modifiers.append([self.getSourceAccount(), selfModifier])
        self.approved = int(tokens[7])
        self.bad = False
    def getModifiers(self):
        return self.modifiers
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
        return self.modifiers[self.modifiers.keys()[0]]
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

class TransactionFactory:
    def __init__(self):
        pass
    def makeTransaction(self, line):
        return Transaction(line)

class Account:
    def __init__(self, name, currency):
        self.name = name
        self.currency = currency
        self.balance = 0.0
        self.income = 0.0
        self.expenses = 0.0
        self.expensesForAccounts = {}
        self.expensesForAccounts[self.getName()] = 0.0
        self.transactions = []
    def getTransactionCount(self):
        return len(self.getTransactions())
    def printAccount(self):
        name = self.getName()
        currency = self.getCurrency()
        balance = self.getBalance()

        print("Account: " + name)
        print("    Currency: " + currency)
        print("    Balance: " + str(balance))
        print("    Income: " +  str(self.income))
        print("    Expenses: " +  str(self.expenses))

        print("    Expenses by beneficiary account")
        expenses = self.expensesForAccounts[self.getName()]
        print("        " + self.getName() + " " + str(expenses))
        for account in self.expensesForAccounts.keys():
            if account == self.getName():
                continue
            expenses = self.expensesForAccounts[account]
            print("        " + account + " " + str(expenses))

        print("    Transactions: " + str(self.getTransactionCount()))

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
        if transaction.getDestinationAccount() != self.getName() \
           and transaction.getSourceAccount() != self.getName():
            print("Error: bad account")
            print(transaction)
            return
        if transaction.getDestinationAccount() == \
           transaction.getSourceAccount():
            print("Error: accounts are the same")
            print(transaction)
            return
        amount = transaction.getAmount()
        if transaction.getDestinationAccount() == self.getName():
            self.balance += amount
            self.income += amount
        elif transaction.getSourceAccount() == self.getName():
            self.balance -= amount
            self.expenses += amount
            # add expenses for each modifier
            modifiers = transaction.getModifiers()
            for modifierPair in modifiers:
                account = modifierPair[0]
                modifier = modifierPair[1]
                amountForNotSelf = modifier * amount

                if account not in self.expensesForAccounts:
                    self.expensesForAccounts[account] = 0.0
                self.expensesForAccounts[account] += amountForNotSelf
        self.transactions.append(transaction)
    def getCurrency(self):
        return self.currency
    def getBalance(self):
        return self.balance
    def getName(self):
        return self.name
    def getTransactions(self):
        return self.transactions
    def getIncome(self):
        return self.income
    def getExpenses(self):
        return self.expenses
    def getExpensesForAccount(self, account):
        if account in self.expensesForAccounts:
            expenses = self.expensesForAccounts[account]
            return expenses
        return 0.0

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
