
from alveare.common.database import DB

class Comment(DB.Model):
    id =      DB.Column(DB.Integer, primary_key=True)
    content = DB.Column(DB.String,  nullable=False)

    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return '<Comment[id:{}]>'.format(self.id)

