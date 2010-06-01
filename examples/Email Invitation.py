#!/usr/bin/python

from __future__ import with_statement # For Python < 2.6

import sys, smtplib, cinesync
from email.mime.text import MIMEText

with cinesync.EventHandler() as evt:
    if evt.is_offline(): sys.exit()

    join_url = cinesync.commands.join_session_url(evt.session_key)
    msg = MIMEText("Come join my cineSync session! Just click here: <%s>\n" % join_url)
    msg["From"] = sys.argv[2]
    msg["To"] = sys.argv[3]
    msg["Subject"] = "Join my cineSync session: %s" % evt.session_key

    s = smtplib.SMTP()
    s.connect(sys.argv[1])
    s.sendmail(msg["From"], msg["To"], msg.as_string())
    s.close()
