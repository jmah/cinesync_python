from __future__ import with_statement

import cinesync
import os, sys, urllib, re, tempfile


# Defines a do_<blah> variant that opens the URL immediately
def opens_with_do(func):
    do_name = "do_" + func.__name__
    def do_func(*args, **kwargs):
        runtime_func = getattr(sys.modules[__name__], func.__name__)
        cinesync.open_url(runtime_func(*args, **kwargs))
    setattr(sys.modules[__name__], do_name, do_func)
    return func


@opens_with_do
def open_session_file(path, merge_with_existing=True):
    op = "merge" if merge_with_existing else "replace"
    return "cinesync://file/%s?path=%s" % (op, urllib.quote_plus(path))

@opens_with_do
def create_session(username=None, password=None):
    u = "cinesync://session/new"
    if username:
        u += "?username=%s" % urllib.quote(username)
        if password:
            u += "&password=%s" % urllib.quote(password)
    return u

@opens_with_do
def join_session(session_key):
    return "cinesync://session/%s" % urllib.quote(session_key)

@opens_with_do
def run_script(script_name, query=None):
    q = ("?" + query) if query else ""
    return "cinesync://script/%s%s" % (urllib.quote(script_name), q)


ILLEGAL_FILE_CHARS = re.compile("[^\w ~!@#\$%&\(\)_\-\+=\[\]\{\}',\.]")

@opens_with_do
def open_session(session, name=None, merge_with_existing=True):
    name = name or "untitled session"
    path = os.path.join(tempfile.gettempdir(), re.sub(ILLEGAL_FILE_CHARS, "_", name) + ".csc")
    with open(path, "w") as f:
        f.write(session.to_xml())
    return open_session_file(f.name, merge_with_existing)
