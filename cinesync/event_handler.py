import cinesync

from optparse import OptionParser


class EventHandler:
    def __init__(self, argv, session):
        self.session = session

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
        self.save_parent = options.save_dir
        self.url = options.url

    def is_offline(self):
        self.session_key == None

    @classmethod
    def call_with_fn(cls, argv, session, fn):
        fn(cls(argv, session))
