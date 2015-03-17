
from alveare.common.database import DB

class TalentPool(DB.Model):
    __pluralname__ = 'talent_pools'

    id = DB.Column(DB.Integer, primary_key=True)

    def __repr__(self):
        return '<TalentPool[id:{}]>'.format(self.id)

