# cineSync Python Library

## Integration Overview

### Commands and Events

cineSync 3.0 introduced new features to integrate with the production pipeline. This is achieved with two concepts: commands and events.

![Commands and Events](http://www.cinesync.com/files/api_commands_events.png)

**Commands** are sent by other applications to cineSync. A command is a URL with the `cinesync:` scheme, so they can be called from a web page or email, or sent by an application or script. Commands in cineSync 3.0:

- Joining a session
- Starting a new session
- Modifying the current session's content (adding new files, changing notes and annotations)
- Running a script configured in cineSync

The syntax for these is described in the command reference.

**Events** are triggered from within cineSync. These run commands, typically a Python or Ruby script. You can always run these manually, or also choose to have them run automatically when certain things change in cineSync. The triggered script has full access to the content of the session, along with some of the surrounding environment (the session key, etc.).

Running event scripts from cineSync requires a cineSync Pro account.

### The Session File

The cineSync session file format holds information about the contents of the session. This is the same format that is generated when selecting "Save Session" from within cineSync. This is an XML-based file, with the goal to represent the session as it was seen on the local computer.

*Backward compatibility note:* The session file format has changed significantly with cineSync 3. cineSync 3 can open sessions saved by older versions of cineSync, but will only write the v3 format.

When cineSync runs a command via an event, it serializes the current session and pipes it to the command. The script can examine the current playlist, notes, annotations, and so on, so it could save them to a shared production database, or access additional information about the active movie.

Additionally, an external script can call a `cinesync:` URL, giving it the path to a session file on disk. cineSync will then open this file and add its contents to the session. This allows creating a session from an external tool, or adding notes from external sources.

The cineSync API libraries (Ruby and Python) provide methods for manipulating and generating the session file format. From other languages, you can manipulate the XML structure directly.

### Event Handler Environment

When cineSync runs a script, it calls it with arguments describing the current environment: the session key, saved frame folder and format. The API provides a standard event handler block that parses these arguments and reads the session file, presenting them as native objects to the rest of the Ruby or Python script. See below for event handler examples.

## Getting Started
### Installing the Library

**Note:** The cineSync Python API requires Python 2.5 or higher.

Install the cineSync package with `easy_install cinesync`. The following examples are marked as "command" or "event handler". Those marked "command" can be run from a shell, or from another application. Scripts marked as "event handler" should be set up in cineSync's preferences and run from the *Session* &gt; *Run Script* menu.

### Joining an Existing Session (command)

This example shows how to join a session, with the key passed as a command-line argument. Save the script as `join.py` and call it as:
`python join.py ASDF1234` (using a valid session key).

    import sys, cinesync
    key = sys.argv[1]
    cinesync.commands.join_session(key)

### Creating a Session (command)

This script creates a session with a single media file, linked to an HTTP URL. Once in cineSync, you will be given the option to download it (or locate it locally).

You can also give a local file path to the MediaFile constructor.

    import cinesync
    s = cinesync.Session()
    file = cinesync.MediaFile("http://cinesync.com/files/sample_qt.mov")
    s.media.append(file)
    cinesync.commands.open_session(s)

### Email a Session Invitation (event handler)

The following script sends an email containing the current session key as a clickable link. (This script is also in the examples folder.)

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

In cineSync, add a script with the command:

    /usr/bin/python /path/to/invite.py smtp.example.com from_me@example.com my_friend@example.com

Adjust the path to the script, and the path to Python (on Windows it will be similar to `C:\Python26\python.exe`). Replace the email addresses and SMTP server as necessary.

### Export Notes to CSV (event handler)

This script is in the `examples` folder of the repository. It will create a CSV file on the Desktop named with the session key, including all notes from the session (frame, media file, and session).

In cineSync, add a script with the command:

    /usr/bin/python "/path/to/Export Notes to CSV.py"

As above, adjust the path to the script, and the path to Python.

## Support

If you have any questions using the cineSync Python library, or with the cineSync integration features in general, please contact [support@cinesync.com](mailto:support@cinesync.com).

## Links

 * [cineSync homepage](http://cinesync.com/)
 * [cineSync support email](mailto:support@cinesync.com)

## Files

 * `cineSync Session v3 Schema.rnc`: Session XML schema in [RELAX NG](http://relaxng.org/) Compact syntax

## Copyright

Copyright (c) 2010 Rising Sun Research Pty Ltd. See LICENSE for details.
