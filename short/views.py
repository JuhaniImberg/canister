import re
from functools import wraps

from bottle import response, request, template, redirect, static_file

from short import app, config, backend
from short.link import Link
from short.errors import *

urlre = re.compile(config["regex-url"])
namere = re.compile(config["regex-name"])


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


def wrap_error(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        ret = None
        try:
            ret = f(*args, **kwds)
        except LinkError as e:
            error(str(e))
            return redirect("/")
        return ret
    return wrapper


@app.get("/")
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


@app.post("/")
@wrap_error
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
        raise InvalidURLError(url)
        return redirect("/")
    # If the name has been specified
    if name and len(name) > 0:
        # If the name doesn't match the regex-name report it
        if name != namere.match(name).group(0):
            raise InvalidNameError(name)

    else:
        # Name wasn't spesified so find another name
        name = backend.next_name()

    backend.set(Link(name=name, url=url))

    set_cookie("url", name)
    return redirect("/")


@app.get("/i/style")
def route_style():
    """
    Returns the stylesheet
    """
    return static_file("style.css", root="static")


@app.get("/i/tos")
def route_style():
    """
    Returns the TOS
    """
    return template("tos", pretty=config["pretty-name"])


@app.get("/i/icon")
def route_style():
    """
    Returns the TOS
    """
    return static_file("favicon.ico", root="static")


@app.get("/i/qr/<name>")
@wrap_error
def route_qr(name):
    """
    Returns a QR code in XML for the name
    """
    link = backend.get(name)
    response.set_header("Content-Type", "image/svg+xml")
    return link.qr()


@app.get("/<name>")
@wrap_error
def route_name(name):
    """
    This route catches all other routes.
    """
    link = backend.get(name)
    backend.visit(link.name)
    return redirect(link.url)
