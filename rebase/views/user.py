from marshmallow import fields
import marshmallow.exceptions as marsh
import sqlalchemy.orm.exc as orm_exc

from rebase.common.schema import RebaseSchema
from rebase.common.database import get_or_make_object, SecureNestedField
from rebase.views.role import RoleSchema

class PhotoSchema(RebaseSchema):
    id =  fields.Integer()
    url = fields.String(required=True)

class UserSchema(RebaseSchema):
    id =            fields.Integer()
    first_name =    fields.String(required=True)
    last_name =     fields.String(required=True)
    email =         fields.Email(required=True)
    password =      fields.String(required=True)
    last_seen =     fields.DateTime(required=True)
    admin =         fields.Boolean(default=False)
    current_role =  SecureNestedField('RoleSchema')
    photo =         SecureNestedField(PhotoSchema, only='url')

    roles = SecureNestedField('RoleSchema', exclude=('user',), many=True)


    def make_object(self, data):
        from rebase.models import User
        if tuple(data.keys()) == ('email',):
            try:
                return User.query.filter(User.email == data.get('email')).one()
            except orm_exc.NoResultFound as error:
                raise marsh.ValidationError('Bad email')
        return get_or_make_object(User, data)

serializer = UserSchema(only=('id','admin','first_name','last_name','email','last_seen','roles', 'current_role', 'photo'))

deserializer = UserSchema(only=('first_name','last_name','email','password'), strict=True)

update_deserializer = UserSchema(only=('first_name','last_name','email','password'))
update_deserializer.make_object = lambda data: data
