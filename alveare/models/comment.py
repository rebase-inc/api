
from alveare.common.database import DB

class Comment(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)

    def __repr__(self):
        return '<Comment[id:{}]>'.format(self.id)

