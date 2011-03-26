"""
Web frontend to gitmarks for use as a bookmarklet.
"""

import bottle
bottle.debug(False)

from bottle import route, run, request, response, template
from gitmark import gitMark
import settings

@route("/")
def index():
    return template("index", port = settings.GITMARKS_WEB_PORT)

@route("/new")
def new():
    url = request.GET.get('url')

    return template("new", url=url, tags=None, message=None, error=None)

@route("/create", method = "POST")
def create():
    url = request.forms.get('url', '').strip()
    tags = request.forms.get('tags', '').strip()
    message = request.forms.get('message', '').strip()
    push = request.forms.get('nopush', True)

    if push == '1':
        push = False

    if not url:
        return template("new", url=url, tags=tags, message=message, error="URL is required.")

    options = {}
    options['tags'] = tags
    options['push'] = push
    options['msg']  = message

    args = [url]

    g = gitMark(options, args)

    return template("create")

run(host="localhost", port=settings.GITMARKS_WEB_PORT, reloader=False)
