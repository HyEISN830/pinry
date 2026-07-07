from xml.etree import ElementTree


XMP_START = b'<x:xmpmeta'
XMP_END = b'</x:xmpmeta>'
MP4_SIGNATURE = b'ftyp'

NS_GCAMERA = 'http://ns.google.com/photos/1.0/camera/'
NS_OPCAMERA = 'http://ns.oplus.com/photos/1.0/camera/'
NS_ITEM = 'http://ns.google.com/photos/1.0/container/item/'


class MotionPhotoPayload(object):
    def __init__(self, video, video_length, source):
        self.video = video
        self.video_length = video_length
        self.source = source


def _attr(element, namespace, name):
    return element.attrib.get('{{{}}}{}'.format(namespace, name))


def _int_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _extract_xmp(data):
    start = data.find(XMP_START)
    if start == -1:
        return None
    end = data.find(XMP_END, start)
    if end == -1:
        return None
    end += len(XMP_END)
    return data[start:end]


def _read_motion_metadata(xmp_bytes):
    try:
        root = ElementTree.fromstring(xmp_bytes)
    except ElementTree.ParseError:
        return None

    motion_photo = False
    source = 'google_motion_photo'
    video_length = None
    for element in root.iter():
        if _attr(element, NS_GCAMERA, 'MotionPhoto') == '1':
            motion_photo = True
        if _attr(element, NS_OPCAMERA, 'OLivePhotoVersion'):
            motion_photo = True
            source = 'op_camera_motion_photo'

        mime = _attr(element, NS_ITEM, 'Mime')
        semantic = _attr(element, NS_ITEM, 'Semantic')
        if mime == 'video/mp4' and semantic == 'MotionPhoto':
            video_length = _int_or_none(_attr(element, NS_ITEM, 'Length'))

        if video_length is None:
            video_length = _int_or_none(_attr(element, NS_OPCAMERA, 'VideoLength'))
        if video_length is None:
            video_length = _int_or_none(_attr(element, NS_GCAMERA, 'MicroVideoOffset'))

    if not motion_photo or not video_length:
        return None
    return {
        'video_length': video_length,
        'source': source,
    }


def extract_motion_photo_payload(field_file):
    with field_file.open('rb') as stream:
        data = stream.read()
    xmp = _extract_xmp(data)
    if xmp is None:
        return None
    metadata = _read_motion_metadata(xmp)
    if metadata is None:
        return None
    video_length = metadata['video_length']
    if video_length <= 0 or video_length >= len(data):
        return None
    video = data[-video_length:]
    if MP4_SIGNATURE not in video[:32]:
        return None
    return MotionPhotoPayload(
        video=video,
        video_length=video_length,
        source=metadata['source'],
    )
