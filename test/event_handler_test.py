#!/usr/bin/python2.5
from __future__ import with_statement

import unittest

import sys
import os

import cinesync


class EventHandlerTest(unittest.TestCase):
    def setUp(self):
        self.online_args = ['myscript.py', '--key=ASDF0000', '--save-format=JPEG', '--save-dir=/tmp/cinesync']
        self.offline_args = ['myscript.py', '--key=_OFFLINE_', '--save-format=JPEG', '--save-dir=/tmp/cinesync']

    def test_loading_session_from_stdin(self):
        handler_run = False
        path = os.path.join('test', 'v3 files', 'v3-basic.csc')
        with open(path) as file:
            with cinesync.EventHandler(self.online_args, file) as evt:
                s = evt.session
                self.assertEqual(s.user_data, 'sessionUserData blah bloo blee')
                self.assertEqual(len(s.media), 3)
                self.assertEqual(s.notes, "These are my session notes.\nnewline.")
                self.assertTrue(s.is_valid())
                handler_run = True
        self.assertTrue(handler_run)

    def test_parsing_args(self):
        handler_run = False
        path = os.path.join('test', 'v3 files', 'v3-basic.csc')
        with open(path) as file:
            with cinesync.EventHandler(self.online_args, file) as evt:
                self.assertFalse(evt.is_offline())
                self.assertEqual(evt.session_key, 'ASDF0000')
                self.assertEqual(evt.save_format, 'JPEG')
                self.assertEqual(evt.save_parent, '/tmp/cinesync')
                handler_run = True
        self.assertTrue(handler_run)
