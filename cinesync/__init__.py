"""
Library for scripting the cineSync collaborative video review tool

Copyright (c) 2010 Rising Sun Research Pty Ltd
All rights reserved.


Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.

    * Neither the name of the Rising Sun Resarch Pty Ltd nor the names of its contributors
      may be used to endorse or promote products derived from this software
      without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

__author__ = 'Jonathon Mah <jmah@cinesync.com>'
__version__ = '0.1'

SESSION_V3_XML_FILE_VERSION = 3
SHORT_HASH_SAMPLE_SIZE = 2048
ALL_FILES_GROUP = 'All Files'
OFFLINE_KEY = '_OFFLINE_'
SESSION_V3_NAMESPACE = 'http://www.cinesync.com/ns/session/3.0'


import os
import sys
import hashlib
import struct

from session import Session
from media_file import MediaFile, GroupMovie, MediaLocator
from frame_annotation import FrameAnnotation
from event_handler import EventHandler
import csc_xml


class CineSyncError(Exception):
    """Base class for errors in the cinesync package."""

class InvalidError(CineSyncError):
    pass

def short_hash(path):
    with open(path, 'rb') as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(0)

        dgst = hashlib.sha1()
        dgst.update(struct.pack('!L', size)[::-1])
        if size <= SHORT_HASH_SAMPLE_SIZE:
            dgst.update(f.read(size))
            dgst.update(struct.pack('x' * (SHORT_HASH_SAMPLE_SIZE - size)))
        else:
            dgst.update(f.read(SHORT_HASH_SAMPLE_SIZE / 2))
            f.seek(-SHORT_HASH_SAMPLE_SIZE / 2, os.SEEK_END)
            dgst.update(f.read(SHORT_HASH_SAMPLE_SIZE / 2))
        return dgst.hexdigest()

def event_handler(fn):
    try:
        session = Session.load(sys.stdin)
    except Exception:
        session = None
    EventHandler.call_with_fn(sys.argv, session, fn)
