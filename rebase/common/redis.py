
from redis import ConnectionPool


POOL = ConnectionPool(host='redis', max_connections=1)


