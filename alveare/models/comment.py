from .review import Review
from .mediation import Mediation

from alveare.common.database import DB

class Comment(DB.Model):
    id =        DB.Column(DB.Integer, primary_key=True)
    content =   DB.Column(DB.String,  nullable=False)

    review_id = DB.Column(DB.Integer, DB.ForeignKey('review.id', ondelete='CASCADE'), nullable=True)
    mediation_id = DB.Column(DB.Integer, DB.ForeignKey('mediation.id', ondelete='CASCADE'), nullable=True)

    def __init__(self, parent, content=None):
        if isinstance(parent, Review):
            self.review = parent
        elif isinstance(parent, Mediation):
            self.mediation = parent
        else:
            raise Exception('Unknown parent type for comment')
        self.content = content

    def __repr__(self):
        abbreviated_content = self.content[0:15]
        if self.content != abbreviated_content:
            abbreviated_content += '...'
        return '<Comment[{}] "{}">'.format(self.id, abbreviated_content)

