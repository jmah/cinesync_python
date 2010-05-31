#!/usr/bin/python2.5

import unittest

import sys, os
import ntpath

import cinesync


class CommandsTest(unittest.TestCase):
    def test_open_session_url(self):
        merge_u = cinesync.commands.open_session_file("My funky! file#name.csc")
        self.assertEqual(merge_u, "cinesync://file/merge?path=My+funky%21+file%23name.csc")

        replace_u = cinesync.commands.open_session_file("My funky! file#name.csc", False)
        self.assertEqual(replace_u, "cinesync://file/replace?path=My+funky%21+file%23name.csc")

    def test_create_session(self):
        self.assertEqual(cinesync.commands.create_session(), "cinesync://session/new")
        self.assertEqual(cinesync.commands.create_session("jon@home"), "cinesync://session/new?username=jon%40home")
        self.assertEqual(cinesync.commands.create_session("jmah", "s3cr!t"), "cinesync://session/new?username=jmah&password=s3cr%21t")
        self.assertEqual(cinesync.commands.create_session(None, "s3cr!t"), "cinesync://session/new")

    def test_join_session(self):
        self.assertEqual(cinesync.commands.join_session("ASDF1234"), "cinesync://session/ASDF1234")
        self.assertEqual(cinesync.commands.join_session("IAM1337"), "cinesync://session/IAM1337")

    def test_run_script(self):
        self.assertEqual(cinesync.commands.run_script("My custom handler"), "cinesync://script/My%20custom%20handler")
        u = cinesync.commands.run_script("My custom handler? {takes query}", "a=1&b=2")
        self.assertEqual(u, "cinesync://script/My%20custom%20handler%3F%20%7Btakes%20query%7D?a=1&b=2")


if __name__ == '__main__':
    unittest.main()
