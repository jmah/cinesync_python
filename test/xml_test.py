#!/usr/bin/python2.5

import unittest

import sys
import os
import xml.etree.cElementTree as ET
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

import cinesync
from cinesync.csc_xml import NS


class XMLTest(unittest.TestCase):
    def test_empty_session(self):
        s = cinesync.Session()
        xml = s.to_xml()
        self.assertTrue(xml)
        doc = ET.fromstring(xml)
        self.assertEqual(doc.tag, NS + 'session')
        self.assertEqual(int(doc.get('version')), cinesync.SESSION_V3_XML_FILE_VERSION)

    def test_invalid_session_fails(self):
        s = cinesync.Session()
        s.media.append(cinesync.MediaFile())
        self.assertFalse(s.is_valid())
        self.assertRaises(cinesync.InvalidError, s.to_xml)

    def test_loading_basic(self):
        path = os.path.join('test', 'v3 files', 'v3-basic.csc')
        with open(path) as file:
            s = cinesync.Session.load(file)
        self.assertEqual(s.file_version, 3)
        self.assertEqual(s.user_data, 'sessionUserData blah bloo blee')
        self.assertEqual(len(s.media), 3)
        self.assertEqual(s.notes, "These are my session notes.\nnewline.")
        self.assertTrue(s.is_valid())

        self.assertTrue(s.media[0].is_valid())
        self.assertEqual(s.media[0].name, '024b_fn_079_v01_1-98.mov')
        self.assertEqual(s.media[0].locator.path, '/Volumes/Scratch/test_files/movies/024b_fn_079_v01_1-98.mov')
        self.assertFalse(s.media[0].active)
        self.assertEqual(s.media[0].current_frame, 1)
        self.assertEqual(s.media[0].user_data, '')
        self.assertEqual(s.media[0].groups, [])

        self.assertTrue(s.media[1].is_valid())
        self.assertEqual(s.media[1].name, 'sample_mpeg4.mp4')
        self.assertEqual(s.media[1].locator.url, 'http://example.com/test_files/movies/sample_mpeg4.mp4')
        self.assertEqual(s.media[1].locator.short_hash, 'e74db5de61fa5483c541a3a3056f22d158b44ace')
        self.assertTrue(s.media[1].active)
        self.assertEqual(s.media[1].current_frame, 65)
        self.assertEqual(s.media[1].user_data, '')
        self.assertEqual(s.media[1].groups, [])

        self.assertTrue(s.media[2].is_valid())
        self.assertEqual(s.media[2].name, 'Test_MH 2fps.mov')
        self.assertEqual(s.media[2].locator.short_hash, 'f9f0c5d3e3e340bcc9486abbb01a71089de9b886')
        self.assertFalse(s.media[2].active)
        self.assertEqual(s.media[2].current_frame, 1)
        self.assertEqual(s.media[2].user_data, 'myPrivateInfo')
        self.assertEqual(s.media[2].groups, [])

    def test_loading_group_movie(self):
        path = os.path.join('test', 'v3 files', 'v3-refmovie.csc')
        with open(path) as file:
            s = cinesync.Session.load(file)
        self.assertEqual(s.file_version, 3)
        self.assertEqual(s.user_data, 'sessionUserData blah bloo blee')
        self.assertEqual(len(s.media), 3)
        self.assertEqual(s.notes, "These are my session notes.\nnewline.")
        self.assertEqual(s.groups, ['myGroup'])
        self.assertTrue(s.is_valid())

        self.assertTrue(s.media[0].is_valid())
        self.assertEqual(s.media[0].name, '024b_fn_079_v01_1-98.mov')
        self.assertEqual(s.media[0].locator.path, '/Volumes/Scratch/test_files/movies/024b_fn_079_v01_1-98.mov')
        self.assertFalse(s.media[0].active)
        self.assertEqual(s.media[0].current_frame, 1)
        self.assertEqual(s.media[0].user_data, '')
        self.assertEqual(s.media[0].groups, ['myGroup'])

        self.assertTrue(s.media[1].is_valid())
        self.assertEqual(s.media[1].name, 'sample_mpeg4.mp4')
        self.assertEqual(s.media[1].locator.url, 'http://example.com/test_files/movies/sample_mpeg4.mp4')
        self.assertEqual(s.media[1].locator.short_hash, 'e74db5de61fa5483c541a3a3056f22d158b44ace')
        self.assertFalse(s.media[1].active)
        self.assertEqual(s.media[1].current_frame, 1)
        self.assertEqual(s.media[1].user_data, '')
        self.assertEqual(s.media[1].groups, [])

        self.assertTrue(s.media[2].is_valid())
        self.assertEqual(s.media[2].group, 'myGroup')
        self.assertFalse(s.media[2].active)
        self.assertEqual(s.media[2].current_frame, 1)
        self.assertEqual(s.media[2].user_data, '')

    def test_loading_higher_version(self):
        xml_str = """<?xml version="1.0" encoding="UTF-8" ?>
            <session xmlns="http://www.cinesync.com/ns/session/3.0" version="4" sessionFeatures="standard">
            </session>
        """
        s = cinesync.Session.load(xml_str, True)
        self.assertFalse(s.is_valid())
        self.assertEqual(s.user_data, '')
        self.assertEqual(s.file_version, 4)
        self.assertEqual(s.notes, '')
        self.assertEqual(s.get_session_features(), 'standard')

    def test_loading_groups(self):
        xml_str = """<?xml version="1.0" encoding="UTF-8" ?>
            <session xmlns="http://www.cinesync.com/ns/session/3.0" version="3" sessionFeatures="standard">
                <group>Group 1</group>
                <group>second&gt;group</group>
                <media userData="media data" currentFrame="12">
                    <name>First movie</name>
                    <locators><shortHash>f9f0c5d3e3e340bcc9486abbb01a71089de9b886</shortHash></locators>
                    <group>Group 1</group>
                </media>
            </session>
        """
        s = cinesync.Session.load(xml_str, True)
        self.assertTrue(s.is_valid())
        self.assertEqual(s.groups, ['Group 1', 'second>group'])
        self.assertEqual(s.media[0].current_frame, 12)
        self.assertEqual(s.media[0].groups, ['Group 1'])

    def test_loading_notes(self):
        xml_str = """<?xml version="1.0" encoding="UTF-8" ?>
            <session xmlns="http://www.cinesync.com/ns/session/3.0" version="3" sessionFeatures="standard">
                <media userData="media data">
                    <name>First movie</name>
                    <locators><path>/does/not/exist.mov</path></locators>
                    <notes>Media notes that come first in the file</notes>
                </media>
                <notes>session notes</notes>
            </session>
        """
        s = cinesync.Session.load(xml_str, True)
        self.assertEqual(s.notes, 'session notes')
        self.assertEqual(s.media[0].current_frame, 1)
        self.assertEqual(s.media[0].user_data, 'media data')
        self.assertEqual(s.media[0].notes, 'Media notes that come first in the file')

    def test_writing_basic(self):
        s = cinesync.Session()
        path = '/path/to/nonexistent/file.mov'
        s.media.append(cinesync.MediaFile(path))
        xml = s.to_xml()
        self.assertTrue(xml)
        doc = ET.fromstring(xml)
        self.assertEqual(doc.tag, NS + 'session')
        self.assertEqual(len(doc.findall(NS + 'media')), 1)
        media_elem = doc.find(NS + 'media')
        self.assertEqual(len(media_elem.findall(NS + 'group')), 0)
        path_elem = media_elem.find('.//%slocators/%spath' % (NS, NS))
        self.assertEqual(path_elem.text, path)

    def test_writing_short_hash_locator(self):
        s = cinesync.Session()
        path = '/Volumes/Oyama/Streams/cineSync Test Files/movies/nasa_shuttle_m420p.mov'
        mf = cinesync.MediaFile(path)
        s.media.append(mf)

        doc = ET.fromstring(s.to_xml())
        media_elem = doc.find(NS + 'media')
        loc_elem = media_elem.find(NS + 'locators')
        self.assertEqual(loc_elem.findtext(NS + 'path'), mf.locator.path)
        self.assertEqual(loc_elem.findtext(NS + 'shortHash'), mf.locator.short_hash)
        self.assertEqual(loc_elem.findtext(NS + 'url'), None)

    def test_writing_url_locator(self):
        s = cinesync.Session()
        url = 'http://example.com/random_file.mov'
        mf = cinesync.MediaFile(url)
        s.media.append(mf)

        doc = ET.fromstring(s.to_xml())
        media_elem = doc.find(NS + 'media')
        loc_elem = media_elem.find(NS + 'locators')
        self.assertEqual(loc_elem.findtext(NS + 'path'), None)
        self.assertEqual(loc_elem.findtext(NS + 'shortHash'), None)
        self.assertEqual(loc_elem.findtext(NS + 'url'), mf.locator.url)


if __name__ == '__main__':
    unittest.main()
