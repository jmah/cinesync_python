#!/usr/bin/python2.6

import sys, os, urllib, tempfile
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cinesync


if len(sys.argv) == 1:
    print >>sys.stderr, 'Usage: %s <file.mov> ...' % sys.argv[0]

session = cinesync.Session()
session.media = [cinesync.MediaFile(path) for path in sys.argv[1:]]
f = tempfile.NamedTemporaryFile(suffix='.csc', delete=False)
f.write(session.to_xml())
f.close()

cinesync.open_url('cinesync://file/merge?path=%s' % urllib.quote_plus(f.name))
