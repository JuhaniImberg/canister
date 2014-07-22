import importlib

from bottle import default_app

from short.config import config
from short.backend import get_backend

app = default_app()
backend = get_backend(config["backend"]["name"])(config["backend"])
import short.views
