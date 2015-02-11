from .review import Review
from .mediation import Mediation

from alveare.common.database import DB

class Comment(DB.Model):
    id =        DB.Column(DB.Integer, primary_key=True)
    content =   DB.Column(DB.String,  nullable=False)
    review_id = DB.Column(DB.Integer, DB.ForeignKey('review.id'), nullable=True)
    mediation_id = DB.Column(DB.Integer, DB.ForeignKey('mediation.id'), nullable=True)

    def __init__(self, parent, content=None):
        if isinstance(parent, Review):
            self.review = parent
        elif isinstance(parent, Mediation):
            self.mediation = parent
        else:
            raise Exception('Unknown parent type for comment')
        self.content = content

    def __repr__(self):
        return '<Comment[{}]>'.format(self.id)

