import cinesync

import types


class FrameAnnotation:
    def __init__(self, frame_num):
        self.frame = frame_num
        self.notes = ''
        self.drawing_objects = []

    def is_default(self):
        return not self.notes and not self.drawing_objects

    def is_valid(self):
        return isinstance(self.frame, (types.IntType, types.LongType)) and self.frame >= 1

    def to_xml(self):
        return cinesync.csc_xml.frame_annotation_to_xml(self)

    @classmethod
    def load(cls, elem):
        return cinesync.csc_xml.frame_annotation_from_xml(elem)
