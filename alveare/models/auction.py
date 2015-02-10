from sqlalchemy.orm import validates

from alveare.common.database import DB

class Auction(DB.Model):

    id =                DB.Column(DB.Integer,   primary_key=True)
    duration =          DB.Column(DB.Integer,   nullable=False)
    finish_work_by =    DB.Column(DB.DateTime,  nullable=False)
    redundancy =        DB.Column(DB.Integer,   nullable=False)

    def __init__(self, duration, finish_work_by, redundancy = 1):
        self.duration = duration
        self.finish_work_by = finish_work_by
        self.redundancy = redundancy

    def __repr__(self):
        return '<Auction[id:{}] finish_work_by={}>'.format(self.id, self.finish_work_by)
    
    @validates('duration')
    def validate_duration(self, field, value):
        if not isinstance(value, int):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, int))
        return value
    
    @validates('redundancy')
    def validate_outcome(self, field, value):
        if not isinstance(value, int):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, int))
        return value

    #@validates('')
    #def validate_outcome(self, field, value):
        #if not isinstance(value, int):
            #raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, int))
        #return value
