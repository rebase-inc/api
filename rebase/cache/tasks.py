from logging import getLogger
from queue import Queue
from sys import exit

from flask_login import login_user

from rebase.common.stopwatch import DebugElapsedTime
from rebase.models import Role


logger = getLogger()


elapsed_time = DebugElapsedTime(start='', stop='Running get_collections took: %f seconds')


def login(role_id):
    role = Role.query.get(role_id)
    if not role:
        error('Unknown role, terminating')
        return
    role.user.set_role(role.id)
    login_user(role.user) # so current_user is properly initialized


def clear_collections_from_redis(role_id):
    from rebase.resources.ticket import get_all_tickets
    from rebase.resources.auction import get_all_auctions
    from rebase.resources.contract import get_all_contracts
    from rebase.resources.review import get_all_reviews
    get_all_tickets.clear_cache(role_id)
    get_all_auctions.clear_cache(role_id)
    get_all_contracts.clear_cache(role_id)
    get_all_reviews.clear_cache(role_id)


def get_collections(role_id):
    from rebase.resources.ticket import get_all_tickets
    from rebase.resources.auction import get_all_auctions
    from rebase.resources.contract import get_all_contracts
    from rebase.resources.review import get_all_reviews
    get_all_tickets(role_id)
    get_all_auctions(role_id)
    get_all_contracts(role_id)
    get_all_reviews(role_id)


def warmup(app, role_id):
    #logger.debug('Wiping out Redis and child cache for role: %d', role_id)
    login(role_id)
    clear_collections_from_redis(role_id)
    app.cache_in_process.clear()
    with elapsed_time:
        get_collections(role_id)


def invalidate_cache(delete_key, keys, changeset):
    '''
    This function removes keys from the cache that match the provided changeset.
    There is a one-to-one match between an item in 'changetset' and one in 'keys' in the
    case of update or delete operations (indirectly PUT/DELETE).
    The more difficult case is when a new object gets created. This object (its hash) is not present
    in the cache, but one of its parent is, so we need to invalidate the parent and the parent's parent and so on.

    'delete_key' is a function to delete keys from 'keys' which is a cache.
    'changeset' contains the list of new/updated/deleted instances' identities (type, ids)
    '''
    #logger.debug('# of cache keys before invalidation: %d', len(keys))
    q = Queue(maxsize=1024)
    # first, flatten the changeset into a dict with each (k,v) => (hash(instance), instance)
    instances_to_invalidate = dict()
    for type_obj, ids in changeset.items():
        for _id in ids:
            identity = (type_obj, _id)
            _hash = hash(str(identity))
            if _hash in keys:
                q.put(_hash)
            else:
                # _id is a new obj that's never been cached, so we need to find its parents
                instance = type_obj.query.get(_id)
                if not instance.__mapper__.relationships:
                    logger.debug('%s was not found in cache and does not have any relationship, skipping invalidation', instance)
                for relationship in instance.__mapper__.relationships:
                    if relationship.direction.name == 'MANYTOONE':
                        parent = getattr(instance, relationship.key, None)
                        if parent:
                            _parent_hash = hash(parent)
                            if _parent_hash in keys:
                                q.put(_parent_hash)
                                #logger.debug('Found parent %s of %s in in-process cache', parent, instance)
            # now empty the q and delete the corresponding keys from the cache
            while not q.empty():
                _hash = q.get()
                for key, parent_hash in keys[_hash]:
                    delete_key(key)
                    q.put(parent_hash)
                del keys[_hash]

    #logger.debug('# of cache keys after invalidation: %d', len(keys))


def incremental(app, role_id, changeset):
    login(role_id)
    clear_collections_from_redis(role_id)
    invalidate_cache(app.cache_in_process.cache.delete, app.cache_in_process.keys, changeset)
    setattr(app.cache_in_process, 'misses', 0)
    with elapsed_time:
        get_collections(role_id)
    #logger.debug('cache misses: %s', app.cache_in_process.misses)


def cooldown(app, role_id):
    logger.info('QUIT')
    exit(0)


def invalidate(app, role_id, changeset):
    '''
    invalidate updates the list of potentially modified model instances 
    contained in 'changeset' and re-computes the cached functions

    Anytime the web server creates/deletes/updates (but not reads) a resource,
    it reads the identity_map of the sqlalchemy session for that request. 
    The keys of the map is the 'changeset'.
    That 'changeset' gets broadcasted to all cache children.

    After the update, the child's identity_map now contains the truth,
    meaning it matches the state of the database at the time of the transaction that produced
    the 'changeset'.
    '''
    logger.debug('invalidate changeset: %s', changeset)
    incremental(app, role_id, changeset)


