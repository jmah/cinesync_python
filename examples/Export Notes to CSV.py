#!/usr/bin/python
#
# This script reads the current session from cineSync and converts all notes
# made on the session, each media file, and each frame to a CSV file on the
# Desktop. This file can then be processed by other scripts or opened in a
# spreadsheet program (Microsoft Excel, OpenOffice.org Calc, Apple Numbers).

from __future__ import with_statement # For Python < 2.6

import sys, os, csv, cinesync


with cinesync.EventHandler() as evt:
    if evt.is_offline():
        filename = 'Notes from offline session.csv'
    else:
        filename = 'Notes from %s.csv' % evt.session_key
    path = os.path.expanduser('~/Desktop/' + filename)

    with open(path, 'wb') as file:
        csv_file = csv.writer(file)
        csv_file.writerow(['Media File', 'Frame', 'Notes']) # Header row

        if evt.session.notes:
            csv_file.writerow(['', '[Session]', evt.session.notes])

        for media_file in evt.session.media:
            if media_file.notes:
                csv_file.writerow([media_file.name, '[Media File]', media_file.notes])

            # Iterate by frame in sorted order
            # (iterating over a dict would otherwise have undefined order)
            for frame in sorted(media_file.annotations.keys()):
                ann = media_file.annotations[frame]
                if ann.notes:
                    csv_file.writerow([media_file.name, ann.frame, ann.notes])
