#!/usr/bin/python2.5

import unittest

import sys, os
import ntpath

import cinesync


class UtilsTest(unittest.TestCase):
    def test_short_hash_with_big_file(self):
        hash = cinesync.short_hash('/Volumes/Oyama/Streams/cineSync Test Files/movies/nasa_shuttle_m420p.mov')
        self.assertEqual(hash, '08e5628d51b14278f73f36afebf0506afc2bfcf8')

    def test_short_hash_with_small_file(self):
        hash = cinesync.short_hash(os.path.join('test', 'small.txt'))
        self.assertEqual(hash, '1e40efb84050f92618e2c430742f44254771cf6b')


class SessionTest(unittest.TestCase):
    def setUp(self):
        self.obj = cinesync.Session()

    def test_file_version(self):
        self.assertEqual(self.obj.file_version, 3)
        self.assertTrue(self.obj.is_valid())
        self.obj.file_version = -1
        self.assertFalse(self.obj.is_valid())

    def test_default_features(self):
        self.assertEqual(self.obj.get_session_features(), 'standard')

    def test_user_data(self):
        self.assertEqual(self.obj.user_data, '')
        self.obj.user_data = 'My custom data'
        self.assertEqual(self.obj.user_data, 'My custom data')

    def test_groups(self):
        self.assertEqual(self.obj.groups, [])
        self.obj.groups.append('My group')
        self.assertEqual(self.obj.groups, ['My group'])

    def test_notes(self):
        self.assertEqual(self.obj.notes, '')
        self.obj.notes = 'asdf'
        self.assertEqual(self.obj.notes, 'asdf')

    def test_media_list(self):
        self.assertEqual(self.obj.media, [])


class MediaFileTest(unittest.TestCase):
    def setUp(self):
        self.obj = cinesync.MediaFile('ftp://ftp.cinesync.com/demo.mov')

    def test_valid_by_default(self):
        self.assertTrue(self.obj.is_valid())

    def test_default_annotations(self):
        self.assertFalse(self.obj.annotations)

    def test_annotations_on_demand(self):
        self.assertEqual(self.obj.annotations, {})
        on_demand = self.obj.annotations[32]
        self.assertTrue(on_demand is not None)
        self.assertEqual(on_demand.notes, '')

        # Check that the instance we have is shared with the annotations dict
        on_demand.notes = 'notes on frame 32'
        self.assertEqual(self.obj.annotations[32].notes, on_demand.notes)

    def test_annotation_valid(self):
        ann = self.obj.annotations[3]
        self.assertTrue(ann.is_valid())
        self.assertTrue(self.obj.is_valid())
        ann2 = self.obj.annotations[-5]
        self.assertFalse(ann2.is_valid())
        self.assertFalse(self.obj.is_valid())
        del self.obj.annotations[-5]
        self.assertTrue(self.obj.is_valid())

    def test_optional_locator_arg(self):
        mf_loc = cinesync.MediaFile('/Volumes/Oyama/Streams/cineSync Test Files/movies/nasa_shuttle_m420p.mov')
        self.assertTrue(mf_loc.is_valid())
        mf_noloc = cinesync.MediaFile()
        self.assertFalse(mf_noloc.is_valid())

    def test_name(self):
        self.assertEqual(self.obj.name, 'demo.mov')
        self.obj.name = ''
        self.assertEqual(self.obj.name, '')
        self.assertFalse(self.obj.is_valid())
        self.obj.name = 'custom_name'
        self.assertEqual(self.obj.name, 'custom_name')
        self.assertTrue(self.obj.is_valid())

        mf_noloc = cinesync.MediaFile()
        self.assertEqual(mf_noloc.name, '')

    def test_user_data(self):
        self.assertEqual(self.obj.user_data, '')
        self.obj.user_data = 'My custom data'
        self.assertEqual(self.obj.user_data, 'My custom data')
        self.assertTrue(self.obj.is_valid())

    def test_active(self):
        self.assertFalse(self.obj.active)
        self.obj.active = True
        self.assertTrue(self.obj.active)
        self.assertTrue(self.obj.is_valid())

    def test_current_frame(self):
        self.assertEqual(self.obj.current_frame, 1)
        self.obj.current_frame = 99
        self.assertEqual(self.obj.current_frame, 99)
        self.assertTrue(self.obj.is_valid())
        self.obj.current_frame = -1
        self.assertEqual(self.obj.current_frame, -1)
        self.assertFalse(self.obj.is_valid())

    def test_groups(self):
        self.assertEqual(self.obj.groups, [])
        self.obj.groups.append('My group')
        self.assertEqual(self.obj.groups, ['My group'])

    def test_notes(self):
        self.assertEqual(self.obj.notes, '')
        self.obj.notes = 'My media notes'
        self.assertEqual(self.obj.notes, 'My media notes')

    def test_features(self):
        self.assertFalse(self.obj.uses_pro_features())


class GroupMovieTest(unittest.TestCase):
    def setUp(self):
        self.obj = cinesync.GroupMovie('grp')

    def test_group(self):
        self.assertEqual(self.obj.group, 'grp')
        self.assertTrue(self.obj.is_valid())
        self.obj.group = ''
        self.assertEqual(self.obj.group, '')
        self.assertFalse(self.obj.is_valid())

        empty = cinesync.GroupMovie('')
        self.assertEqual(empty.group, '')
        self.assertFalse(empty.is_valid())
        empty.group = cinesync.ALL_FILES_GROUP
        self.assertTrue(empty.is_valid())

    def test_current_frame(self):
        self.assertEqual(self.obj.current_frame, 1)
        self.obj.current_frame = 99
        self.assertEqual(self.obj.current_frame, 99)
        self.assertTrue(self.obj.is_valid())
        self.obj.current_frame = -1
        self.assertEqual(self.obj.current_frame, -1)
        self.assertFalse(self.obj.is_valid())

    def test_groups(self):
        self.assertEqual(self.obj.groups, [])
        self.obj.groups.append('My other group')
        self.assertEqual(self.obj.groups, ['My other group'])

    def test_features(self):
        self.assertTrue(self.obj.uses_pro_features())


class MediaLocatorTest(unittest.TestCase):
    def test_empty_locator(self):
        ml = cinesync.MediaLocator()
        self.assertFalse(ml.is_valid())
        self.assertTrue(ml.path is None)
        self.assertTrue(ml.url is None)
        self.assertTrue(ml.short_hash is None)

    def test_url_locator(self):
        url = 'http://example.com/random_file.mov'
        ml = cinesync.MediaLocator(url)
        self.assertTrue(ml.is_valid())
        self.assertTrue(ml.path is None)
        self.assertEqual(ml.url, url)
        self.assertTrue(ml.short_hash is None)

        import urlparse
        comps = urlparse.urlparse(ml.url)
        self.assertEqual(comps.scheme, 'http')
        self.assertEqual(comps.hostname, 'example.com')
        self.assertEqual(comps.path, '/random_file.mov')
        self.assertEqual(comps.geturl(), url)

    def test_file_locator(self):
        path = '/Volumes/Oyama/Streams/cineSync Test Files/movies/nasa_shuttle_m420p.mov'
        ml = cinesync.MediaLocator(path)
        self.assertTrue(ml.is_valid())
        self.assertEqual(ml.path, path)
        self.assertTrue(ml.url is None)
        self.assertEqual(ml.short_hash, '08e5628d51b14278f73f36afebf0506afc2bfcf8')

    def test_nonexist_file_locator(self):
        path = '/path/to/nonexistent/file.mov'
        ml = cinesync.MediaLocator(path)
        self.assertTrue(ml.is_valid())
        self.assertEqual(ml.path, path)
        self.assertTrue(ml.url is None)
        self.assertTrue(ml.short_hash is None)

    def test_dos_file_locator(self):
        path = r'C:\path\to\myMovie.mov'
        ml = cinesync.MediaLocator(path, ntpath)
        self.assertTrue(ml.is_valid())
        self.assertEqual(ml.path, path)
        self.assertTrue(ml.url is None)
        self.assertTrue(ml.short_hash is None)

    def test_hash_locator(self):
        hash = '08e5628d51b14278f73f36afebf0506afc2bfcf8'
        ml = cinesync.MediaLocator(hash)
        self.assertTrue(ml.is_valid())
        self.assertTrue(ml.path is None)
        self.assertTrue(ml.url is None)
        self.assertEqual(ml.short_hash, hash)

    def test_relative_path_conversion(self):
        rel_path = '../nonexist-test.mov'
        abs_path = os.path.abspath(rel_path)
        ml = cinesync.MediaLocator(rel_path)
        self.assertEqual(ml.path, abs_path)


class SessionMediaTest(unittest.TestCase):
    def setUp(self):
        self.obj = cinesync.Session()

    def test_features_with_group_movie(self):
        self.assertEqual(self.obj.get_session_features(), 'standard')
        self.obj.media.append(cinesync.GroupMovie(cinesync.ALL_FILES_GROUP))
        self.assertEqual(self.obj.get_session_features(), 'pro')
        del self.obj.media[0]
        self.assertEqual(self.obj.get_session_features(), 'standard')

    def test_validity(self):
        self.assertTrue(self.obj.is_valid())
        mf = cinesync.MediaFile()
        self.assertFalse(mf.is_valid())
        self.obj.media.append(mf)
        self.assertFalse(self.obj.is_valid())
        mf.name = 'asdf'
        mf.locator.path = 'asdf.mov'
        self.assertTrue(mf.is_valid())
        self.assertTrue(self.obj.is_valid())


class FrameAnnotationTest(unittest.TestCase):
    def setUp(self):
        self.obj = cinesync.FrameAnnotation(5)

    def test_frame_valid(self):
        self.assertEqual(self.obj.frame, 5)
        self.assertTrue(self.obj.is_valid())
        self.assertFalse(cinesync.FrameAnnotation(0).is_valid()) # 1-based, so 0 is invalid
        self.assertFalse(cinesync.FrameAnnotation(-5).is_valid())
        self.assertFalse(cinesync.FrameAnnotation('three').is_valid())

    def test_notes(self):
        self.assertEqual(self.obj.notes, '')
        self.obj.notes = 'asdf'
        self.assertEqual(self.obj.notes, 'asdf')

    def test_drawing_objects(self):
        self.assertEqual(len(self.obj.drawing_objects), 0)

    def test_default(self):
        self.assertTrue(self.obj.is_default())
        self.obj.notes = 'asdf'
        self.assertFalse(self.obj.is_default())


if __name__ == '__main__':
    unittest.main()
