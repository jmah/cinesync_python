#!/usr/bin/python2.6

import sys, os, urllib, tempfile
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cinesync

if len(sys.argv) == 1:
    print >>sys.stderr, 'Usage: %s <file.mov> ...' % sys.argv[0]
    sys.exit(1)

# Create the session and add media from command-line arguments
session = cinesync.Session()
session.media = [cinesync.MediaFile(path) for path in sys.argv[1:]]

# Write session to temporary file
f = tempfile.NamedTemporaryFile(suffix='.csc', delete=False)
f.write(session.to_xml())
f.close()

# Ask cineSync to add the session to its current state
cinesync.open_url('cinesync://file/merge?path=%s' % urllib.quote_plus(f.name))
