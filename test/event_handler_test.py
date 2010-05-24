#!/usr/bin/python2.5

import unittest

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

import cinesync


class EventHandlerTest(unittest.TestCase):
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
            save_stdin = sys.stdin
            sys.stdin = file
            cinesync.event_handler(my_handler)
            sys.stdin = save_stdin
        self.assertTrue(handler_run[0])
