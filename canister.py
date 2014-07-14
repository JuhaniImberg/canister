from bottle import response, request, run, template, static_file, debug, get, post, request, redirect
from redis import StrictRedis
from hashids import Hashids
from config import config
import re

redis = StrictRedis(host=config["redis-host"], port=config["redis-port"], db=0)
hashids = Hashids(salt=config["hashids-salt"])
urlre = re.compile("^(https?):\/\/[-a-zA-Z0-9+&@#\/%?=~_|!:,.;]*[-a-zA-Z0-9+&@#\/%=~_|]")

@get("/")
def route_index():
    url = request.get_cookie("url")
    error = request.get_cookie("error")
    last_url = last_error = None
    if error:
        last_error = error
        response.set_cookie("error", "", expires=0)
    if url:
        last_url = url
        response.set_cookie("url", "", expires=0)
    return template("index", last_url=last_url, last_error=last_error)

@post("/")
def route_add():
    url = request.forms.get("url")
    name = request.forms.get("name")
    if not url or not urlre.match(url):
        response.set_cookie("error", "That's not a URL.", max_age=5)
        return redirect("/")
    if name and len(name) > 0:
        prev = redis.get("canister:"+name)
        if prev:
            response.set_cookie("error", "That name is already in use.", max_age=5)
            return redirect("/")
    else:
        while 1:
            num = redis.incr("canister:num")
            name = hashids.encrypt(num)
            if not redis.exists(name):
                break

    redis.set("canister:"+name, url)

    response.set_cookie("url", config["base-url"] + name, max_age=5)
    return redirect("/")

@get("/style")
def route_style():
    return static_file("style.css", root="static")

@get("/<name>")
def route_name(name):
    url = redis.get("canister:"+name)
    if url:
        redis.incr("canister:"+ name +":clicks")
        return redirect(url.decode("utf-8"))
    response.set_cookie("error", "No such entry.", max_age=5)
    return redirect("/")

if __name__ == "__main__":
    debug(True)
    run(host=config["server-host"], port=config["server-port"], server=config["server"])