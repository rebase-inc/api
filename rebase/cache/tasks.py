from functools import partial
from logging import info, debug
from sys import exit


from rebase.common.database import DB
from rebase.common.stopwatch import Elapsed


def warmup():
    from rebase.cache.role import ROLE
    from rebase.memoize import cache
    from rebase.resources.auction import get_all_auctions
    cache.delete_memoized(get_all_auctions, ROLE.id)
    with Elapsed(partial(info, 'warmup: running get_all_auctions for {} took %f seconds'.format(ROLE.id))):
        get_all_auctions(ROLE.id)

def cooldown():
    info('QUIT')
    exit(0)

def invalidate(changeset):
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
    warmup()
