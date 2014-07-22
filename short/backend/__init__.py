from short.backend.redis_backend import RedisBackend

backends = {
    "redis": RedisBackend
}


def get_backend(name):
    return backends[name]
