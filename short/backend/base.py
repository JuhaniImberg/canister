class Backend(object):

    def __init__(self, config):
        self.config = config

    def next_name(self):
        raise NotImplementedError()

    def set(self, link):
        raise NotImplementedError()

    def get(self, name):
        raise NotImplementedError()

    def visit(self, name):
        raise NotImplementedError()
