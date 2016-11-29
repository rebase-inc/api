from flask_restful import Resource
from flask_login import login_required, current_user

from rebase.models import GithubAccount
from rebase.views import github_account as views
from rebase.common.database import DB
from rebase.common.rest import get_collection, add_to_collection

class GithubAccountCollection(Resource):
    model = GithubAccount
    serializer = views.serializer
    deserializer = views.deserializer
    url = '/{}'.format(model.__pluralname__)

    @login_required
    def get(self):
        return get_collection(self.model, self.serializer, current_user.current_role.id)

    @login_required
    def post(self):
        return add_to_collection(self.model, self.deserializer, self.serializer)
