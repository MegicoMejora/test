from abc import ABC, abstractmethod
from datetime import datetime


class Transaction(ABC):
    def __init__(self, account_id, amount):
        self.account_id = account_id
        self.amount = amount
        self.timestamp = datetime.now()

    @abstractmethod
    def execute(self, account):
        pass

class DepositTransaction(Transaction):
    def execute(self, account):
        account.deposit(self.amount)
        return "Deposit successful."

class WithdrawalTransaction(Transaction):
    def execute(self, account):
        if account.withdraw(self.amount):
            return "Withdrawal successful."
        return "Insufficient funds."
