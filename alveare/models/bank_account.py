
from alveare.common.database import DB

class BankAccount(DB.Model):
    id =            DB.Column(DB.Integer, primary_key=True)
    routing_number = DB.Column(DB.String, nullable=False)
    account_number = DB.Column(DB.String, nullable=False)

    def __init__(self, routing_number, account_number):
        self.routing_number = routing_number
        self.account_number = account_number

    def __repr__(self):
        return '<BankAccount[id:{}] routing={} account={}>'.format(self.id, self.routing_number, self.account_number)

