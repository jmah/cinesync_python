#!/usr/bin/python2.5

import unittest

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

import cinesync


class MockEnvironment:
    def __init__(self, argv, stdin):
        self.mock_argv = argv
        self.mock_stdin = stdin

    def __enter__(self):
        self.save_argv = sys.argv
        self.save_stdin = sys.stdin
        sys.argv = self.mock_argv
        sys.stdin = self.mock_stdin

    def __exit__(self, type, value, traceback):
        sys.stdin = self.save_stdin
        sys.argv = self.save_argv

class EventHandlerTest(unittest.TestCase):
    def setUp(self):
        self.online_args = ['myscript.py', '--key=ASDF0000', '--save-format=JPEG', '--save-dir=/tmp/cinesync']
        self.offline_args = ['myscript.py', '--key=_OFFLINE_', '--save-format=JPEG', '--save-dir=/tmp/cinesync']

    def test_loading_session_from_stdin(self):
        handler_run = [False]
        def my_handler(evt):
            s = evt.session
            self.assertEqual(s.user_data, 'sessionUserData blah bloo blee')
            self.assertEqual(len(s.media), 3)
            self.assertEqual(s.notes, "These are my session notes.\nnewline.")
            self.assertTrue(s.is_valid())
            handler_run[0] = True

        path = os.path.join('test', 'v3 files', 'v3-basic.csc')
        with open(path) as file:
            with MockEnvironment(self.online_args, file):
                cinesync.event_handler(my_handler)
        self.assertTrue(handler_run[0])
