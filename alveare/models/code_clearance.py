
from alveare.common.database import DB

class CodeClearance(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    pre_approved = DB.Column(DB.Boolean, nullable=False)

    def __init__(self, pre_approved):
        self.pre_approved = pre_approved

    def __repr__(self):
        return '<CodeClearance[id:{}] pre_approved={}>'.format(self.id, self.pre_approved)

