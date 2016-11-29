from logging import getLogger

from ..app import create
from ..common.aws import exists as s3_exists
from ..common.database import DB
from ..models import Contractor, User, GithubAccount, GithubUser
from ..skills.aws_keys import profile_key
from ..skills.population import get_rankings, s3_get, s3_put
from ..skills.impact_client import ImpactClient

IMPACT_CLIENT = ImpactClient()

logger = getLogger(__name__)


def update_user_rankings(github_user, private=True, contractor_id=None, get=s3_get, exists=s3_exists, put=s3_put):
    user_data_key = profile_key(github_user)
    new_user_data = get(user_data_key)
    profile_with_rankings = new_user_data
    rankings = get_rankings(github_user, get=get, exists=exists)
    profile_with_rankings['rankings'] = rankings
    put(user_data_key, profile_with_rankings)
    if private:
        app = create()
        with app.app_context():
            if contractor_id:
                contractor = Contractor.query.get(contractor_id)
            else:
                contractors = Contractor.query.join(User).join(GithubAccount).join(GithubUser).filter_by(login='rapha-opensource')
                assert contractors
                contractor = contractors[-1]
            if not contractor:
                logger.error('Could not find a Contractor for Github user %s', github_user)
            else:
                contractor.skill_set.skills = {}
                for package, rank in rankings.items():
                    impact = IMPACT_CLIENT.score(*package.split('.'))
                    contractor.skill_set.skills[package] = { 'impact': impact, 'rank': rank }
                DB.session.commit()
