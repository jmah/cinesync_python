import cinesync
import cinesync.media_file
import sys
import types
from StringIO import StringIO

try:
    from lxml import etree as ET
    USING_LXML = True
except ImportError:
    import xml.etree.cElementTree as ET
    USING_LXML = False

NS = '{%s}' % cinesync.SESSION_V3_NAMESPACE
DRAWING_OBJECT_TAGS = ['line', 'erase', 'circle', 'arrow', 'text']


# Modifies its argument in-place
def strip_namespace(elem):
    for e in elem.getiterator():
        if e.tag.startswith(NS):
            e.tag = e.tag[len(NS):]
    return elem


# eSession = element session {
#   attribute version { xsd:integer { minInclusive = "3" } } &
#   attribute sessionFeatures { "standard" | "pro" } &
#   aUserData? &
#   eGroup* &
#   eNotes? &
#   eMedia* }

def session_to_xml(session):
    if not session.is_valid():
        raise cinesync.InvalidError('Cannot convert an invalid session to XML')
    root = ET.Element('session', xmlns=cinesync.SESSION_V3_NAMESPACE,
                      version=str(cinesync.SESSION_V3_XML_FILE_VERSION),
                      sessionFeatures=session.get_session_features())
    if session.chat_elem is not None:
        root.append(strip_namespace(session.chat_elem))
    if session.stereo_elem is not None:
        root.append(strip_namespace(session.stereo_elem))
    for media_file in session.media:
        root.append(media_file.to_xml())
    for grp_name in session.groups:
        ET.SubElement(root, 'group').text = grp_name
    if session.notes: ET.SubElement(root, 'notes').text = session.notes
    if session.user_data: root.set('userData', session.user_data)
    if USING_LXML:
        return ET.tostring(root, xml_declaration=True, encoding='utf-8', pretty_print=True)
    else:
        return ET.tostring(root, 'utf-8')


def session_from_xml(str_or_file, silent=False):
    stream = StringIO(str_or_file) if isinstance(str_or_file, types.StringTypes) else str_or_file
    doc = ET.parse(stream)
    elem = doc.getroot()

    # Do a few checks (the user should have already confirmed that the
    # document conforms to the schema, but we'll try to fail early in case)
    if not elem.tag == (NS + 'session'):
        raise cinesync.CineSyncError('Expected to find root <session> element with attribute xmlns="%s"' % cinesync.SESSION_V3_NAMESPACE)

    doc_version = int(elem.get('version'))
    if doc_version > cinesync.SESSION_V3_XML_FILE_VERSION:
        if not silent:
            print >> sys.stderr, 'Warning: Loading session file with a newer version (%d) than this library (%d)' % (doc_version, cinesync.SESSION_V3_XML_FILE_VERSION)

    session = cinesync.Session()
    session.file_version = doc_version
    session.user_data = elem.get('userData') or ''
    session.groups = [grp.text for grp in elem.findall(NS + 'group')]
    session.notes = elem.findtext(NS + 'notes') or ''
    session.chat_elem = elem.find(NS + 'chat')
    session.stereo_elem = elem.find(NS + 'stereo')
    session.media = [cinesync.media_file.MediaBase.load(media_elem) for media_elem in elem.findall(NS + 'media')]
    return session


# MediaBase =
#   aUserData? &
#   attribute active { tBool }? &
#   attribute currentFrame { tFrameNumber }? &
#   eGroup* &
#   ePlayRange?

def media_from_xml(elem):
    return group_movie_from_xml(elem) if elem.find(NS + 'groupMovie') is not None else media_file_from_xml(elem)

def init_media_common(elem, media_obj):
    media_obj.user_data = elem.get('userData') or ''
    media_obj.active = elem.get('active') == 'true'
    media_obj.groups = [grp.text for grp in elem.findall(NS + 'group')]
    media_obj.current_frame = int(elem.get('currentFrame') or 1)

    play_range_elem = elem.find(NS + 'playRange')
    if play_range_elem is not None:
        media_obj.play_range = cinesync.PlayRange.load(play_range_elem)

def media_base_to_xml(media):
    elem = ET.Element('media')
    if media.user_data: elem.set('userData', media.user_data)
    if media.active: elem.set('active', 'true')
    if media.current_frame != 1: elem.set('currentFrame', media.current_frame)
    if not media.play_range.is_default(): elem.append(media.play_range.to_xml())

    for group_name in media.groups:
        ET.SubElement(elem, 'group').text = group_name
    return elem


# eMedia |= element media {
#   # Normal media file
#   MediaBase &
#   element name { xsd:string { minLength = "1" } } &
#   element locators { eLocator+ } &
#   eNotes? &
#   eZoomState? &
#   ePixelRatio? &
#   eMask? &
#   eColorGrading? &
#   eFrameAnnotation* }

def media_file_from_xml(elem):
    mf = cinesync.MediaFile()
    init_media_common(elem, mf)
    mf.name = elem.findtext(NS + 'name')
    mf.locator = cinesync.MediaLocator.load(elem.find(NS + 'locators'))
    mf.notes = elem.findtext(NS + 'notes') or ''

    for ann_elem in elem.findall(NS + 'annotation'):
        frame = int(ann_elem.get('frame'))
        mf.annotations[frame] = cinesync.FrameAnnotation.load(ann_elem)

    mf.zoom_state_elem = elem.find(NS + 'zoomState')
    mf.pixel_ratio_elem = elem.find(NS + 'pixelRatio')
    mf.mask_elem = elem.find(NS + 'mask')
    mf.color_grading_elem = elem.find(NS + 'colorGrading')

    return mf

def media_file_to_xml(mf):
    elem = media_base_to_xml(mf)
    ET.SubElement(elem, 'name').text = mf.name
    elem.append(locator_to_xml(mf.locator))

    if mf.notes: ET.SubElement(elem, 'notes').text = mf.notes
    for ann in mf.annotations.values():
        if not ann.is_default():
            elem.append(ann.to_xml())

    if mf.zoom_state_elem is not None:
        elem.append(strip_namespace(mf.zoom_state_elem))
    if mf.pixel_ratio_elem is not None:
        elem.append(strip_namespace(mf.pixel_ratio_elem))
    if mf.mask_elem is not None:
        elem.append(strip_namespace(mf.mask_elem))
    if mf.color_grading_elem is not None:
        elem.append(strip_namespace(mf.color_grading_elem))

    return elem


# eMedia |= element media {
#   # Group movie
#   MediaBase &
#   element groupMovie { eGroup } }

def group_movie_from_xml(elem):
    gm = cinesync.GroupMovie(elem.findtext(NS + 'groupMovie/' + NS + 'group'))
    init_media_common(elem, gm)
    return gm

def group_movie_to_xml(gm):
    elem = media_base_to_xml(gm)
    gm_elem = ET.SubElement(elem, 'groupMovie')
    ET.SubElement(gm_elem, 'group').text = gm.group
    return elem


# eLocator |= element path       { tFilePath }
# eLocator |= element shortHash  { tShortHash }
# eLocator |= element url        { tURL }

def media_locator_from_xml(elem):
    loc = cinesync.MediaLocator()
    if elem.findtext(NS + 'path'): loc.path = elem.findtext(NS + 'path')
    if elem.findtext(NS + 'shortHash'):  loc.short_hash = elem.findtext(NS + 'shortHash')
    if elem.findtext(NS + 'url'): loc.url = elem.findtext(NS + 'url')
    return loc

def locator_to_xml(loc):
    if not loc.is_valid():
        raise cinesync.InvalidError('Cannot convert an invalid locator to XML')
    elem = ET.Element('locators')
    if loc.path: ET.SubElement(elem, 'path').text = loc.path
    if loc.short_hash: ET.SubElement(elem, 'shortHash').text = loc.short_hash
    if loc.url: ET.SubElement(elem, 'url').text = loc.url
    return elem


# ePlayRange = element playRange {
#   element inFrame       { attribute value { tFrameNumber } } &
#   element outFrame      { attribute value { tFrameNumber } } &
#   element playOnlyRange { aBoolValue } }

def play_range_from_xml(elem):
    play_range = cinesync.PlayRange()
    play_range.in_frame = int(elem.find(NS + 'inFrame').get('value'))
    play_range.out_frame = int(elem.find(NS + 'outFrame').get('value'))
    play_range.play_only_range = elem.find(NS + 'playOnlyRange').get('value') == 'true'
    return play_range

def play_range_to_xml(play_range):
    if not play_range.is_valid():
        raise cinesync.InvalidError('Cannot convert an invalid play range to XML')
    if play_range.is_default():
        return None
    elem = ET.Element('playRange')
    ET.SubElement(elem, 'inFrame').set('value', str(play_range.in_frame))
    ET.SubElement(elem, 'outFrame').set('value', str(play_range.out_frame))
    only = 'true' if play_range.play_only_range else 'false'
    ET.SubElement(elem, 'playOnlyRange').set('value', only)
    return elem


# eFrameAnnotation = element annotation {
#   attribute frame { tFrameNumber } &
#   eNotes? &
#   eObject* }

def frame_annotation_from_xml(elem):
    frame = int(elem.get('frame'))
    ann = cinesync.FrameAnnotation(frame)
    ann.notes = elem.findtext(NS + 'notes') or ''
    for tag in DRAWING_OBJECT_TAGS:
        for draw_elem in elem.findall(NS + tag):
            ann.drawing_objects.append(strip_namespace(draw_elem))
    return ann

def frame_annotation_to_xml(ann):
    if not ann.is_valid():
        raise cinesync.InvalidError('Cannot convert an invalid frame annotation to XML')
    elem = ET.Element('annotation', frame=str(ann.frame))
    if ann.notes: ET.SubElement(elem, 'notes').text = ann.notes
    for xml_obj in ann.drawing_objects:
        elem.append(xml_obj)
    return elem
