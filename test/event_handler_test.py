#!/usr/bin/python2.5
from __future__ import with_statement

import unittest

import sys
import os

import cinesync


class EventHandlerTest(unittest.TestCase):
    def setUp(self):
        self.example_path = os.path.join('test', 'v3 files', 'v3-basic.csc')
        self.online_args = ['myscript.py', '--key=ASDF0000', '--save-format=JPEG', '--save-dir=/tmp/cinesync']
        self.offline_args = ['myscript.py', '--key=_OFFLINE_', '--save-format=PNG', '--save-dir=/tmp/cinesync']
        self.url_args = ['myscript.py', '--key=URL1111', '--save-format=JPEG', '--url=cinesync://script/myscript?q=hi']

    def test_loading_session_from_stdin(self):
        handler_run = False
        with open(self.example_path) as file:
            with cinesync.EventHandler(self.online_args, file) as evt:
                s = evt.session
                self.assertEqual(s.user_data, 'sessionUserData blah bloo blee')
                self.assertEqual(len(s.media), 3)
                self.assertEqual(s.notes, "These are my session notes.\nnewline.")
                self.assertEqual(evt.url, None)
                self.assertTrue(s.is_valid())
                handler_run = True
        self.assertTrue(handler_run)

    def test_parsing_args(self):
        handler_run = False
        with open(self.example_path) as file:
            with cinesync.EventHandler(self.online_args, file) as evt:
                self.assertFalse(evt.is_offline())
                self.assertEqual(evt.session_key, 'ASDF0000')
                self.assertEqual(evt.save_format, 'JPEG')
                self.assertEqual(evt.save_parent, '/tmp/cinesync')
                self.assertEqual(evt.url, None)
                handler_run = True
        self.assertTrue(handler_run)

    def test_offline_args(self):
        handler_run = False
        with open(self.example_path) as file:
            with cinesync.EventHandler(self.offline_args, file) as evt:
                self.assertTrue(evt.is_offline())
                self.assertEqual(evt.session_key, None)
                self.assertEqual(evt.save_format, 'PNG')
                self.assertEqual(evt.save_parent, '/tmp/cinesync')
                self.assertEqual(evt.url, None)
                handler_run = True
        self.assertTrue(handler_run)

    def test_url_args(self):
        with open(self.example_path) as file:
            with cinesync.EventHandler(self.url_args, file) as evt:
                self.assertFalse(evt.is_offline())
                self.assertEqual(evt.session_key, 'URL1111')
                self.assertEqual(evt.save_format, 'JPEG')
                self.assertEqual(evt.url, 'cinesync://script/myscript?q=hi')
