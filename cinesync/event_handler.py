import cinesync

import sys, os
from optparse import OptionParser


class EventHandler:
    def __init__(self, argv=sys.argv, stdin=sys.stdin):
        try:
            self.session = cinesync.Session.load(stdin)
        except Exception:
            self.session = None

        parser = OptionParser()
        parser.add_option('--key')
        parser.add_option('--save-format')
        parser.add_option('--save-dir')
        parser.add_option('--url')
        (options, rest_args) = parser.parse_args(argv[1:])

        if options.key is None: raise cinesync.CineSyncError('--key argument is required')
        if options.save_format is None: raise cinesync.CineSyncError('--save-format argument is required')
        self.session_key = options.key if options.key != cinesync.OFFLINE_KEY else None
        self.save_format = options.save_format
        self.save_ext = { 'JPEG': 'jpg', 'PNG': 'png' }[self.save_format]
        self.save_parent = options.save_dir
        self.url = options.url

    def is_offline(self):
        return self.session_key == None

    def saved_frame_path(self, media_file, frame):
        if self.save_parent is None: return None
        if not media_file.annotations[frame].drawing_objects: return None

        base = '%s-%05d' % (media_file.name, frame)
        i = 1; p2 = None
        while True:
            p = p2
            p2, i = self.__saved_frame_ver_path(base, i)
            if not os.path.exists(p2):
                return p

    def __saved_frame_ver_path(self, base, version):
        v = ' (%d)' % version if version > 1 else ''
        basename = base + v + '.' + self.save_ext
        return (os.path.join(self.save_parent, basename), version + 1)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass
