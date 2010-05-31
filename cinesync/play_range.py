import cinesync

import types


class PlayRange:
    def __init__(self):
        self.in_frame = None
        self.out_frame = None
        self.play_only_range = True

    def is_default(self):
        return (self.in_frame is None) and (self.out_frame is None) and self.play_only_range

    def is_valid(self):
        return self.is_default() or \
            isinstance(self.in_frame, (types.IntType, types.LongType)) and \
            isinstance(self.out_frame, (types.IntType, types.LongType)) and \
            self.in_frame >= 1 and self.out_frame >= 1 and self.out_frame >= self.in_frame

    def to_xml(self):
        return cinesync.csc_xml.play_range_to_xml(self)

    @classmethod
    def load(cls, elem):
        return cinesync.csc_xml.play_range_from_xml(elem)
