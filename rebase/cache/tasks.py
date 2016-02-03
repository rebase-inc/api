from functools import partial
from logging import info, debug, error
from queue import Queue
from sys import exit, getsizeof

from flask.ext.login import login_user

from rebase.cache.model_ids import ModelIds
from rebase.common.database import DB
from rebase.common.stopwatch import Elapsed
from rebase.models import Role


def login(role_id):
    role = Role.query.get(role_id)
    if not role:
        error('Unknown role, terminating')
        return
    role.user.set_role(role.id)
    login_user(role.user) # so current_user is properly initialized


def warmup(app, role_id, main_state):
    from rebase.resources.auction import get_all_auctions
    login(role_id)
    app.cache_in_redis.clear()
    app.cache_in_process.clear()
    with Elapsed(partial(info, 'warmup: running get_all_auctions for {} took %f seconds'.format(role_id))):
        get_all_auctions(role_id)
    main_state['loaded_model_ids'] = ModelIds(DB.session.identity_map.keys())
    #debug('Keys: %s', app.cache_in_process.keys)
    debug('# of cache keys: %d', len(app.cache_in_process.keys))
    debug('Size of cache keys: %d', getsizeof(app.cache_in_process.keys))
    return main_state


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
    debug('# of cache keys before invalidation: %d', len(keys))
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
                instance = type_obj.query.get(*_id)
                for fk in instance.__table__.foreign_keys:
                    parent = getattr(instance, fk.column.table.name, None)
                    if parent:
                        _parent_hash = hash(parent)
                        if _parent_hash in keys:
                            q.put(_parent_hash)
                        else:
                            # that means we need to implement a recursive search...
                            raise Exception('Parent obj not in cache')
            # now empty the q and delete the corresponding keys from the cache
            while not q.empty():
                _hash = q.get()
                for key, parent_hash in keys[_hash]:
                    delete_key(key)
                    q.put(parent_hash)
                del keys[_hash]

    debug('# of cache keys after invalidation: %d', len(keys))


def incremental(app, role_id, changeset):
    from rebase.resources.auction import get_all_auctions
    login(role_id)
    app.cache_in_redis.clear()
    invalidate_cache(app.cache_in_process.cache.delete, app.cache_in_process.keys, changeset)
    with Elapsed(partial(info, 'incremental: running get_all_auctions for {} took %f seconds'.format(role_id))):
        get_all_auctions(role_id)
    #debug('Keys: %s', app.cache_in_process.keys)
    debug('# of cache keys: %d', len(app.cache_in_process.keys))
    debug('Size of cache keys: %d bytes', getsizeof(app.cache_in_process.keys))
    return ModelIds([])


def cooldown(app, role_id, main_state):
    info('QUIT')
    exit(0)
    return main_state # never reached, but keeps the looks functional :)


def invalidate(app, role_id, main_state, changeset):
    '''
    invalidate updates the list of potentially modified model instances 
    contained in 'changeset' and re-computes the cached functions

    The invalidation mechanism:
    a child maintains a list of loaded model instances's ids (a.k.a. database rows),
    in main_state['loaded_model_ids']. Note this is a list of tuples of (type, ids), no other data,
    which means the size of the list is in the hundreds of bytes only.
    This list is simply 'db.session.identity_map.keys()'.

    Anytime the web server creates/deletes/updates (but not reads) a resource,
    it creates a small identity_map for that request. 
    The keys of the map is the 'changeset'.
    That 'changeset' gets broadcasted to all cache children.
    If the intersection of 'changeset' with the main_state['loaded_model_ids'] of a given child is
    not void, that child must update its cache.

    After the update, the child's identity_map now contains the truth,
    meaning it matches the state of the database at the time of the transaction that produced
    the 'changeset'.
    '''
    debug('invalidate changeset: %s', changeset)
    #debug('invalidate loaded: %s', main_state['loaded_model_ids'])
    #intersection = changeset & main_state['loaded_model_ids']
    #debug('Intersection: %s', intersection)
    #from rebase.models.project import Project
    #if Project.__mapper__.class_ not in intersection:
        #debug('No meaningful intersection, skipping invalidation')
        #return main_state
    main_state['loaded_model_ids'] = incremental(app, role_id, changeset)
    return main_state
