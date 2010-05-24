import cinesync
import cinesync.media_file
import sys
import types
from StringIO import StringIO
import xml.etree.cElementTree as ET

NS = '{%s}' % cinesync.SESSION_V3_NAMESPACE


# eSession = element session {
#   attribute version { xsd:integer { minInclusive = "3" } } &
#   attribute sessionFeatures { "standard" | "pro" } &
#   aUserData? &
#   eGroup* &
#   eNotes? &
#   eMedia* }

def session_to_xml(sess):
    if not sess.is_valid():
        raise cinesync.InvalidError('Cannot convert an invalid session to XML')
    return '<?xml version="1.0" ?><session xmlns="%s" version="%d"></session>' % (cinesync.SESSION_V3_NAMESPACE, cinesync.SESSION_V3_XML_FILE_VERSION)


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
    session.media = [cinesync.media_file.MediaBase.load(media_elem) for media_elem in elem.findall(NS + 'media')]
    return session


# MediaBase =
#   aUserData? &
#   attribute active { tBool }? &
#   attribute currentFrame { tFrameNumber }? &
#   eGroup* &
#   ePlayRange?

def media_from_xml(elem):
    return group_movie_from_xml(elem) if elem.find(NS + 'groupMovie') else media_file_from_xml(elem)

def init_media_common(elem, media_obj):
    media_obj.user_data = elem.get('userData') or ''
    media_obj.active = elem.get('active') == 'true'
    media_obj.notes = elem.findtext(NS + 'notes') or ''
    media_obj.groups = [grp.text for grp in elem.findall(NS + 'group')]
    media_obj.current_frame = int(elem.get('currentFrame') or 1)

def media_file_from_xml(elem):
    mf = cinesync.MediaFile()
    init_media_common(elem, mf)
    mf.name = elem.findtext(NS + 'name')
    mf.locator = cinesync.MediaLocator.load(elem.find(NS + 'locators'))
    return mf

def group_movie_from_xml(elem):
    gm = cinesync.GroupMovie(elem.findtext(NS + 'groupMovie/' + NS + 'group'))
    init_media_common(elem, gm)
    return gm


# eLocator |= element path       { tFilePath }
# eLocator |= element shortHash  { tShortHash }
# eLocator |= element url        { tURL }

def media_locator_from_xml(elem):
    loc = cinesync.MediaLocator()
    if elem.findtext(NS + 'path'): loc.path = elem.findtext(NS + 'path')
    if elem.findtext(NS + 'shortHash'):  loc.short_hash = elem.findtext(NS + 'shortHash')
    if elem.findtext(NS + 'url'): loc.url = elem.findtext(NS + 'url')
    return loc
