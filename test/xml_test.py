#!/usr/bin/python2.5

import unittest

import sys
import os
import xml.etree.cElementTree as ET

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
        self.assertEqual(doc.get('sessionFeatures'), s.get_session_features())
        self.assertEqual(doc.get('userData'), None)
        self.assertEqual(doc.find(NS + 'notes'), None)

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
        self.assertEqual(s.media[2].notes, 'These notes on the last movie.')
        self.assertEqual(s.media[2].annotations[1].notes, 'This is a note on the first frame of the last movie.')
        self.assertEqual(s.media[2].annotations[88].notes, '')

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

    def test_preserving_drawing_objects(self):
        path = os.path.join('test', 'v3 files', 'v3-groups.csc')
        with open(path) as file:
            s = cinesync.Session.load(file)
        self.assertEqual(s.file_version, 3)
        self.assertEqual(s.notes, "")
        self.assertTrue(s.is_valid())

        mf = s.media[0]
        self.assertEqual(len(mf.annotations), 13)
        self.assertTrue(mf.annotations[1].drawing_objects[0].tag in cinesync.csc_xml.DRAWING_OBJECT_TAGS, 'Expected namespace to be stripped from drawing element')

        doc = ET.fromstring(s.to_xml())
        self.assertEqual(len(doc.findall(NS + 'media')), len(s.media))
        self.assertEqual(len(doc.findall(NS + 'group')), len(s.groups))
        self.assertEqual(len(doc.find(NS + 'media').findall(NS + 'annotation')), 13)
        first_ann_elem = doc.find(NS + 'media').find(NS + 'annotation')

    def test_writing_basic(self):
        s = cinesync.Session()
        path = '/path/to/nonexistent/file.mov'
        s.media.append(cinesync.MediaFile(path))
        xml = s.to_xml()
        self.assertTrue(xml)
        doc = ET.fromstring(xml)
        self.assertEqual(doc.tag, NS + 'session')
        self.assertEqual(doc.get('sessionFeatures'), s.get_session_features())
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

    def test_writing_groups(self):
        s = cinesync.Session()
        s.groups = ['Draft', 'Final']
        mf = cinesync.MediaFile('http://example.com/random_file.mov')
        mf.groups.append('Final')
        s.media.append(mf)
        s.media.append(cinesync.MediaFile('http://example.com/random_file_2.mov'))

        doc = ET.fromstring(s.to_xml())
        top_groups = doc.findall(NS + 'group')
        self.assertEqual(len(top_groups), 2)
        self.assertTrue(any([g.text == 'Draft' for g in top_groups]))
        self.assertTrue(any([g.text == 'Final' for g in top_groups]))

        media_elems = doc.findall(NS + 'media')
        self.assertEqual(len(media_elems[0].findall(NS + 'group')), 1)
        self.assertEqual(media_elems[0].findtext(NS + 'group'), mf.groups[0])

        self.assertEqual(len(media_elems[1].findall(NS + 'group')), 0)

    def test_writing_notes(self):
        s = cinesync.Session()
        s.notes = 'asdf'
        mf = cinesync.MediaFile('http://example.com/random_file.mov')
        mf.notes = 'fancy media notes!'
        s.media.append(mf)
        doc = ET.fromstring(s.to_xml())
        self.assertEqual(doc.findtext(NS + 'notes'), s.notes)
        self.assertEqual(doc.find(NS + 'media').findtext(NS + 'notes'), mf.notes)

    def test_writing_user_data(self):
        s = cinesync.Session()
        s.user_data = 'asdf'
        mf = cinesync.MediaFile('http://example.com/random_file.mov')
        mf.user_data = '{"id":"1234QWERTY"}'
        s.media.append(mf)

        doc = ET.fromstring(s.to_xml())
        self.assertEqual(doc.get('userData'), s.user_data)
        self.assertEqual(doc.find(NS + 'media').get('userData'), mf.user_data)

    def test_writing_frame_notes(self):
        s = cinesync.Session()
        mf = cinesync.MediaFile('http://example.com/random_file.mov')
        mf.annotations[33].notes = 'A note on frame 33'
        s.media.append(mf)

        doc = ET.fromstring(s.to_xml())
        ann_elem = doc.find(NS + 'media').find(NS + 'annotation')
        self.assertEqual(ann_elem.get('frame'), str(33))
        self.assertEqual(ann_elem.findtext(NS + 'notes'), 'A note on frame 33')


if __name__ == '__main__':
    unittest.main()
