#!/usr/bin/python2.6

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cinesync

if len(sys.argv) == 1:
    print >>sys.stderr, 'Usage: %s <file.mov> ...' % sys.argv[0]
    sys.exit(1)

# Create the session and add media from command-line arguments
session = cinesync.Session()
session.media = [cinesync.MediaFile(path) for path in sys.argv[1:]]

# Ask cineSync to add the session to its current state
cinesync.commands.do_open_session(session)
