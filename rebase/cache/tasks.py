from functools import partial
from logging import info, debug, error
from sys import exit

from flask.ext.login import login_user

from rebase.cache.model_ids import ModelIds
from rebase.common.database import DB
from rebase.common.stopwatch import Elapsed
from rebase.models import Role


def get_role(role_id):
    role = Role.query.get(role_id)
    if not role:
        error('Unknown role, terminating')
        return
    role.user.set_role(role.id)
    login_user(role.user)
    return role


def warmup(main_state):
    from flask import current_app
    from rebase.resources.auction import get_all_auctions
    role = get_role(main_state['id'])
    current_app.cache_in_redis.clear()
    current_app.cache_in_process.clear()
    with Elapsed(partial(info, 'warmup: running get_all_auctions for {} took %f seconds'.format(role.id))):
        get_all_auctions(role.id)
    main_state['loaded_model_ids'] = ModelIds(DB.session.identity_map.keys())
    return main_state


def cooldown(main_state):
    info('QUIT')
    exit(0)


def invalidate(main_state, changeset):
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
    #debug('Invalidating changeset: %s', changeset)
    #debug('Current loaded ids: %s', main_state['loaded_model_ids'])
    intersection = changeset & main_state['loaded_model_ids']
    debug('Intersection: %s', intersection)
    from rebase.models.project import Project
    if type(Project) not in intersection:
        debug('No meaningful intersection, skipping invalidation')
        return main_state
    debug('Updating get_all_auctions cache after invalidation')
    return warmup(main_state)
