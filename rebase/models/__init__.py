from inspect import isclass
from sys import modules

from rebase.models.bid_limit import *
from rebase.models.contract import *
from rebase.models.bid import *
from rebase.models.arbitration import *
from rebase.models.auction import *
from rebase.models.bank_account import *
from rebase.models.code_clearance import *
from rebase.models.code_repository import *
from rebase.models.comment import *
from rebase.models.contractor import *
from rebase.models.credit import *
from rebase.models.debit import *
from rebase.models.feedback import *
from rebase.models.github_project import *
from rebase.models.github_account import *
from rebase.models.github_repository import *
from rebase.models.internal_ticket import *
from rebase.models.remote_ticket import *
from rebase.models.github_ticket import *
from rebase.models.mediation import *
from rebase.models.organization import *
from rebase.models.project import *
from rebase.models.remote_project import *
from rebase.models.remote_work_history import *
from rebase.models.review import *
from rebase.models.skill_requirement import *
from rebase.models.skill_set import *
from rebase.models.nomination import *
from rebase.models.talent_pool import *
from rebase.models.term_sheet import *
from rebase.models.ticket import *
from rebase.models.ticket_match import *
from rebase.models.ticket_set import *
from rebase.models.ticket_snapshot import *
from rebase.models.user import *
from rebase.models.work import *
from rebase.models.work_offer import *
from rebase.models.manager import *
from rebase.models.bid import *
from rebase.models.job_fit import *
from rebase.models.photo import *

# TODO simplify this with inspect.getmembers (see example in common.utils.RebaseResource.all_models)
models = modules[__name__]
loaded_references = models.__dict__.copy()
for klass in loaded_references.values():
    if isclass(klass) and issubclass(klass, PermissionMixin):
        klass.setup_queries(models)
