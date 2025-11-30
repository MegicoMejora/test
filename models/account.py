class Account:
    def __init__(self, account_id, user_id, balance=0.0):
        self.account_id = account_id
        self.user_id = user_id
        self.__balance = balance

    def get_balance(self):
        return self.__balance

    def deposit(self, amount):
        self.__balance += amount
    def withdraw(self, amount):
        
        if amount <= self.__balance:
            self.__balance -= amount
            return True
        return False
