from redis import StrictRedis
from hashids import Hashids

from short import config
from short.link import Link
from short.backend.base import Backend
from short.errors import *

hashids = Hashids(salt=config["hashids-salt"])


class RedisBackend(Backend):

    def __init__(self, config):
        super(RedisBackend, self).__init__(config)
        self.redis = StrictRedis(host=config.get("host", "localhost"),
                                 port=config.get("port", 6379),
                                 db=config.get("db", 0))
        self.namespace = config.get("namespace", "short:")

    def furl(self, name):
        return self.namespace + "url:" + name

    def fvisits(self, name):
        return self.namespace + "visits:" + name

    def next_name(self):
        name = None
        while 1:
            name = hashids.encrypt(
                self.redis.incr(self.namespace + "meta:num"))
            if not self.redis.exists(self.furl(name)):
                break
        return name

    def set(self, link):
        if self.redis.exists(self.furl(link.name)):
            raise NameUnavailableError(link.name)
        self.redis.set(self.furl(link.name), link.url)
        self.redis.set(self.fvisits(link.name), 0)

    def get(self, name):
        rawlink = self.redis.get(self.furl(name))
        if not rawlink:
            raise NotFoundError(name)
        link = Link(name=name,
                    url=rawlink.decode("utf-8"),
                    visits=int(
                        self.redis.get(self.fvisits(name)) or 0
                    ))
        return link

    def visit(self, name):
        self.redis.incr(self.fvisits(name))
