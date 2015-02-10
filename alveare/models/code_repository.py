
from alveare.common.database import DB

class CodeRepository(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)

    def __repr__(self):
        return '<CodeRepository[id:{}]>'.format(self.id)

