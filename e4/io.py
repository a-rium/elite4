import io

from ..e4 import XML_Tag, XML_Document, XML_FragmentType


def dump_tag(tag: XML_Tag, out: io.StringIO):
    inside = tag.name
    if tag.attributes:
        inside += ' ' + ' '.join((f'{key}="{value}"' for key, value in tag.attributes.items()))
    if tag.fragments:
        out.write(f'<{inside}>')
    else:
        out.write(f'<{inside}/>')


def dump(root: XML_Tag, out: io.StringIO):
    dump_tag(root, out)
    if root.fragments:
        for fragment in root.fragments:
            if fragment.kind == XML_FragmentType.ELEMENT:
                dump(fragment.data, out)
            else:
                out.write(fragment.data)
        out.write(f'</{root.name}>')


def dump_document(document: XML_Document, out: io.StringIO):
    dump(document.root, out)
