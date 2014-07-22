class LinkError(RuntimeError):

    def __init__(self):
        pass


class NotFoundError(LinkError):

    def __init__(self, name):
        self.value = "No entry found for '{}'.".format(name)

    def __str__(self):
        return self.value


class NameUnavailableError(LinkError):

    def __init__(self, name):
        self.value = "The name '{}' is unavailable.".format(name)

    def __str__(self):
        return self.value


class InvalidNameError(LinkError):

    def __init__(self, name):
        self.value = "The name '{}' is not valid.".format(name)

    def __str__(self):
        return self.value


class InvalidURLError(LinkError):

    def __init__(self, url):
        self.value = "The url '{}' is not valid.".format(url)

    def __str__(self):
        return self.value
