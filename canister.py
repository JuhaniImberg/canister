#!/usr/bin/env python3

from bottle import response, request, run, template, static_file, debug, get, post, request, redirect
from redis import StrictRedis
from hashids import Hashids
from config import config
import re

redis = StrictRedis(host=config["redis-host"], port=config["redis-port"], db=0)
hashids = Hashids(salt=config["hashids-salt"])
urlre = re.compile("^(https?):\/\/[-a-zA-Z0-9+&@#\/%?=~_|!:,.;]*[-a-zA-Z0-9+&@#\/%=~_|]")
namere = re.compile("([a-zA-Z_\-+]){1,32}")

def set_cookie(name, value):
    response.set_cookie(name, value, max_age=5)

def get_cookie(name, value):
    if request.get_cookie(name):
        response.set_cookie(name, "", expires=0)
        return request.get_cookie(name)
    else:
        return value

def error(value):
    set_cookie("error", value)

@get("/")
def route_index():
    """
    """
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
                    form_url=form_url, form_name=form_name)

@post("/")
def route_add():
    url = request.forms.get("url")
    name = request.forms.get("name")
    set_cookie("form_url", url)
    set_cookie("form_name", name)
    if not url or not urlre.match(url):
        error("That's not a URL.")
        return redirect("/")
    if name and len(name) > 0:
        prev = redis.get("canister:"+name)
        if prev or name == "/style":
            error("That name is already in use.")
            return redirect("/")
        if name != namere.match(name).group(0):
            error("That name doesn't match to ([a-zA-Z_\-+]){1,32}")
            return redirect("/")
    else:
        while 1:
            num = redis.incr("canister:num")
            name = hashids.encrypt(num)
            if not redis.exists(name):
                break

    redis.set("canister:"+name, url)

    set_cookie("url", config["base-url"] + name)
    return redirect("/")

@get("/style")
def route_style():
    return static_file("style.css", root="static")

@get("/<name>")
def route_name(name):
    """
    This route catches all other routes
    """
    url = redis.get("canister:"+name)
    if url:
        redis.incr("canister:"+ name +":clicks")
        return redirect(url.decode("utf-8"))
    error("No such entry.")
    return redirect("/")

if __name__ == "__main__":
    debug(True)
    run(host=config["server-host"], port=config["server-port"], server=config["server"])