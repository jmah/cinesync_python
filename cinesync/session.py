import cinesync

class Session:
    def __init__(self):
        self.file_version = cinesync.SESSION_V3_XML_FILE_VERSION
        self.user_data = ''
        self.media = []
        self.groups = []
        self.notes = ''
        self.chat_elem = None
        self.stereo_elem = None

    def get_session_features(self):
        return 'pro' if any([m.uses_pro_features() for m in self.media]) \
                        or (self.stereo_elem is not None) else 'standard'

    def is_valid(self):
        return self.file_version == cinesync.SESSION_V3_XML_FILE_VERSION and \
               all([m.is_valid() for m in self.media])

    def to_xml(self):
        return cinesync.csc_xml.session_to_xml(self)

    @classmethod
    def load(cls, str_or_file, silent=False):
        return cinesync.csc_xml.session_from_xml(str_or_file, silent)
