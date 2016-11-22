from functools import partial

from redis import StrictRedis

from rq.job import get_current_job


def crawl_prefix(contractor_id):
    return 'rebase:contractor:{}:crawl:'.format(contractor_id)


def to_be_scanned_repos_key(contractor_id):
    return crawl_prefix(contractor_id)+'to_be_scanned_repos'


def scanning_repo_key(contractor_id):
    return crawl_prefix(contractor_id)+'scanning'


def scanned_repos_key(contractor_id):
    return crawl_prefix(contractor_id)+'scanned_repos'


def get_redis():
    job = get_current_job()
    return job.connection if job else StrictRedis('redis')


def notify_to_be_scanned_repos(contractor_id, repos):
    key = to_be_scanned_repos_key(contractor_id)
    pipe = get_redis().pipeline()
    pipe.delete(key)
    pipe.delete(scanning_repo_key(contractor_id))
    pipe.delete(scanned_repos_key(contractor_id))
    pipe.lpush(key, *repos)
    pipe.execute()


def notify_scanning(contractor_id, repo):
    assert contractor_id
    redis = get_redis()
    key = scanning_repo_key(contractor_id)
    if repo:
        redis.set(key, repo)
    else:
        redis.delete(key)


def notify_scanned_repos(contractor_id, repo):
    assert contractor_id
    assert isinstance(repo, str)
    get_redis().lpush(scanned_repos_key(contractor_id), repo)


def expire_notifications_keys(contractor_id):
    assert contractor_id
    pipe = get_redis().pipeline()
    ttl = 300 # seconds
    pipe.expire(to_be_scanned_repos_key(contractor_id), ttl)
    pipe.expire(scanned_repos_key(contractor_id), ttl)
    pipe.execute()


def NoOp(*args):
    pass


def notifications_for(contractor_id):
    if contractor_id:
        return (
            partial(fn, contractor_id) for fn in (
                notify_to_be_scanned_repos,
                notify_scanning,
                notify_scanned_repos,
                expire_notifications_keys,
            )
        )
    else:
        return (NoOp, NoOp, NoOp, NoOp)


def decode(repos):
    return [ repo.decode() for repo in repos ]


def get_notification(redis, contractor_id):
    pipe = redis.pipeline()
    pipe.lrange(to_be_scanned_repos_key(contractor_id), 0, -1)
    pipe.get(scanning_repo_key(contractor_id))
    pipe.lrange(scanned_repos_key(contractor_id), 0, -1)
    to_be_scanned, scanning, scanned = pipe.execute()
    return {
        'to_be_scanned': decode(to_be_scanned),
        'scanning': scanning.decode() if scanning else '',
        'scanned': decode(scanned),
    }


