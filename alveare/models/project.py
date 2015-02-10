
from alveare.common.database import DB

class Project(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)

    def __repr__(self):
        return '<Project[id:{}]>'.format(self.id)

