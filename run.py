from bottle import debug, run

from short import app, config

debug(True)
run(host=config["server-host"],
    port=config["server-port"],
    server=config["server"])
