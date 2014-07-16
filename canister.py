#!/usr/bin/env python3

from bottle import (response, request, run, template, static_file,
                    debug, get, post, request, redirect, default_app)
from redis import StrictRedis
from hashids import Hashids
from config import config
import re
import qrcode
import qrcode.image.svg
from xml.etree import ElementTree
try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO
import sys

redis = StrictRedis(host=config["redis-host"], port=config["redis-port"], db=0)
hashids = Hashids(salt=config["hashids-salt"])
urlre = re.compile(config["regex-url"])
namere = re.compile(config["regex-name"])


"""
Redis keys:

    canister:meta:*         - meta info
    canister:links:*        - key is name and value is url
    canister:links:*:clicks - number of clicks for that key
"""


def set_cookie(name, value):
    """Shorthand to setting a very short lived cookie"""
    response.set_cookie(name, value, max_age=5)


def get_cookie(name, value):
    """Get a cookie or return the value. Expires the cookie if used"""
    if request.get_cookie(name):
        response.set_cookie(name, "", expires=0)
        return request.get_cookie(name)
    else:
        return value


def error(value):
    """Sets a error cookie"""
    set_cookie("error", value)


@get("/")
def route_index():
    url = request.get_cookie("url")
    error = request.get_cookie("error")
    last_url = last_error = None
    form_url = form_name = ""
    last_url = get_cookie("url", None)
    if error:
        last_error = error
        response.set_cookie("error", "", expires=0)
    form_url = get_cookie("form_url", "")
    form_name = get_cookie("form_name", "")
    return template("index",
                    last_url=last_url, last_error=last_error,
                    form_url=form_url, form_name=form_name,
                    pretty=config["pretty-name"], base_url=config["base-url"])


@post("/")
def route_add():
    """
    This route does most of the heavy work.
    """
    # Extract parameters from form
    url = request.forms.get("url")
    name = request.forms.get("name")
    # Set those as cookies if we come back later
    set_cookie("form_url", url)
    set_cookie("form_name", name)
    # If there is no url report it as a error
    if not url or not urlre.match(url):
        error("That's not a URL.")
        return redirect("/")
    # If the name has been specified
    if name and len(name) > 0:
        prev = redis.get("canister:links:"+name)
        # If there is a previous entry with that name report it
        if prev or name == "i":
            error("That name is already in use.")
            return redirect("/")
        # If the name doesn't match the regex-name report it
        if name != namere.match(name).group(0):
            error("That name doesn't match to ([a-zA-Z_\-+]){1,32}")
            return redirect("/")
    else:
        # Name wasn't spesified so find another name
        while 1:
            num = redis.incr("canister:meta:num")
            name = hashids.encrypt(num)
            if not redis.exists(name):
                break

    # Finally add the url to redis
    redis.set("canister:links:"+name, url)
    redis.set("canister:links:"+name+":clicks", 0)

    set_cookie("url", name)
    return redirect("/")


@get("/i/style")
def route_style():
    """
    Returns the stylesheet
    """
    return static_file("style.css", root="static")


@get("/i/tos")
def route_style():
    """
    Returns the TOS
    """
    return template("tos", pretty=config["pretty-name"])


@get("/i/qr/<name>")
def route_qr(name):
    """
    Returns a QR code in XML for the name
    """
    url = redis.get("canister:links:"+name)
    if url:
        response.set_header("Content-Type", "image/svg+xml")
        img = qrcode.make(config["base-url"] + name,
                          image_factory=qrcode.image.svg.SvgPathImage)
        img._img.append(img.make_path())
        return ElementTree.tostring(img._img, encoding='utf8', method='xml')
    error("No such entry.")
    return redirect("/")


@get("/<name>")
def route_name(name):
    """
    This route catches all other routes.
    """
    url = redis.get("canister:links:"+name)
    if url:
        # If we find a match, increase it's click count
        redis.incr("canister:links:"+ name +":clicks")
        # And redirect to that url
        return redirect(url.decode("utf-8"))
    # Else show a error
    error("No such entry.")
    return redirect("/")

if __name__ == "__main__":
    debug(True)
    run(host=config["server-host"], port=config["server-port"], server=config["server"])

app = bottle.default_app()