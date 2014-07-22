from short.backend.redis import RedisBackend

backends = {
    "redis": RedisBackend
}


def get_backend(name):
    return backends[name]
