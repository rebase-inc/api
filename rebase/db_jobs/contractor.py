from logging import getLogger

from ..app import create
from ..common.aws import exists as s3_exists
from ..common.database import DB
from ..models import Contractor, User, GithubAccount, GithubUser
from ..skills.aws_keys import profile_key, public_profile_key
from ..skills.population import get_rankings, s3_get, s3_put
from ..skills.impact_client import ImpactClient


IMPACT_CLIENT = ImpactClient()


LOGGER = getLogger(__name__)


def update_user_rankings(
    github_user,
    private=True,
    contractor_id=None,
    get=s3_get,
    exists=s3_exists,
    put=s3_put
):
    user_data_key = profile_key(github_user) if private else public_profile_key(github_user)
    new_user_data = get(user_data_key)
    profile_with_rankings = new_user_data
    rankings = get_rankings(github_user, private, get=get, exists=exists)
    profile_with_rankings['rankings'] = rankings
    put(user_data_key, profile_with_rankings)
    if private:
        app = create()
        with app.app_context():
            if contractor_id:
                contractor = Contractor.query.get(contractor_id)
            else:
                contractors = Contractor.query.join(User).join(GithubAccount).join(GithubUser).filter_by(login=github_user)
                assert contractors
                contractor = contractors[-1]
            if not contractor:
                LOGGER.error('Could not find a Contractor for Github user %s', github_user)
            else:
                contractor.skill_set.skills = {}
                for tech, rank in rankings.items():
                    LOGGER.debug('getting score for {}'.format(tech)) 
                    impact = IMPACT_CLIENT.score(*tech.split('.', maxsplit=2))
                    contractor.skill_set.skills[tech] = { 'impact': impact, 'rank': rank }
                DB.session.commit()


