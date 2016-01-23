from functools import partial
from logging import info, debug, error
from sys import exit

from flask.ext.login import login_user

from rebase.common.database import DB
from rebase.common.stopwatch import Elapsed
from rebase.models import Role

def get_role(role_id):
    info('Loading Role(%d)', role_id)
    role = Role.query.get(role_id)
    if not role:
        error('Unknown role, terminating')
        return
    role.user.set_role(role.id)
    login_user(role.user)
    return role

def warmup(role_id):
    from rebase.memoize import cache
    from rebase.resources.auction import get_all_auctions
    role = get_role(role_id)
    cache.delete_memoized(get_all_auctions, role.id)
    with Elapsed(partial(info, 'warmup: running get_all_auctions for {} took %f seconds'.format(role.id))):
        get_all_auctions(role.id)

def cooldown(role_id):
    info('QUIT')
    exit(0)

def invalidate(role_id, changeset):
    '''
    invalidate updates the list of potentially modified model instances 
    contained in 'changeset' and re-computes the cached functions

    The invalidation mechanism:
    a child maintains a list of loaded model instances (a.k.a. database rows), via
    its global sqlalchemy session.
    This list is simply 'db.session.identity_map'.

    Anytime the web server creates/deletes/updates (but not reads) a resource,
    it creates a small identity_map for that request. This is the 'changeset'.
    That 'changeset' gets broadcasted to all cache children.
    If the intersection of 'changeset' with the global identity_map of a given child is
    not void, that child must update and unionize with the 'changeset'.

    After the update+union has happened, the child's identity_map now contains the truth,
    meaning it matches the state of the database at the time of the transaction that produced
    the 'changeset'.

    '''
    #debug('Invalidating changeset:')
    #debug(changeset)
    #debug('Current DB.identity_map:')
    #debug(tuple(DB.session.identity_map.keys()))
    info('Updating get_all_auctions cache after invalidation')
    warmup(role_id)
