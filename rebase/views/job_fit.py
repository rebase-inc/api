from math import sqrt

from marshmallow import fields, post_load
from rebase.common.schema import RebaseSchema
from rebase.common.database import get_or_make_object, SecureNestedField
from rebase.common.utils import get_model_primary_keys
from rebase.models import JobFit
from rebase.views.nomination import NominationSchema

class JobFitSchema(RebaseSchema):

    contractor_id =  fields.Integer()
    ticket_set_id =  fields.Integer()
    score =          fields.Method('get_score')

    ticket_matches = SecureNestedField('TicketMatchSchema', only=('skill_requirement_id', 'skill_set_id', 'score'), many=True)
    nomination =     SecureNestedField('NominationSchema',  only=('contractor_id',        'ticket_set_id'))

    _primary_keys = get_model_primary_keys(JobFit)

    @classmethod
    def get_similarity(cls, ticket_match):
        dot_product = 0.0
        skill_set_magnitude = 0.0
        skill_requirement_magnitude = 0.0
        for skill, skill_requirement_value in ticket_match.skill_requirement.skills.items():
            skill_set_value = ticket_match.skill_set.skills[skill] if skill in ticket_match.skill_set.skills else 0
            dot_product += skill_set_value * skill_requirement_value
            skill_set_magnitude += skill_set_value * skill_set_value
            skill_requirement_magnitude += skill_requirement_value * skill_requirement_value
        if skill_requirement_magnitude == 0 or skill_set_magnitude == 0:
            return 0
        else:
            cosine_similarity = dot_product / (sqrt(skill_set_magnitude) * sqrt(skill_requirement_magnitude))
            cosine_similarity *= min(sqrt(skill_set_magnitude/skill_requirement_magnitude), 1)
            return (1 + cosine_similarity) / 2

    def get_score(self, obj):
        score = float(sum(self.get_similarity(tm) for tm in obj.ticket_matches))/max(len(obj.ticket_matches), 1)
        return score

    @post_load
    def make_job_fit(self, data):
        return get_or_make_object(JobFit, data, self._primary_keys)

deserializer =          JobFitSchema()
serializer =            JobFitSchema()
update_deserializer =   JobFitSchema(only=('score',))
update_deserializer.make_object = lambda data: data
