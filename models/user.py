class User:
    def __init__(self, user_id, name, password):
        self.user_id = user_id
        self.name = name
        self.password = password


class Customer(User):
    def __init__(self, user_id, name, password, account):
        super().__init__(user_id, name, password)
        self.account = account
