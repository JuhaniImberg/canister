import qrcode
import qrcode.image.svg
from xml.etree import ElementTree
try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO

from short import config


class Link(object):

    def __init__(self, name="", url="", visits=0):
        self.name = name
        self.url = url
        self.visits = visits

    def qr(self):
        img = qrcode.make(config["base-url"] + self.name,
                          image_factory=qrcode.image.svg.SvgPathImage)
        img._img.append(img.make_path())
        return ElementTree.tostring(img._img, encoding='utf8', method='xml')

    def __repr__(self):
        return "{}: {} ({} visits)".format(self.name, self.url, self.visits)

    def __str__(self):
        return repr(self)
