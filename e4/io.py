import io

from e4 import XML_Tag, XML_Document


def dump_tag(tag: XML_Tag, out: io.StringIO):
    inside = tag.name
    if tag.attributes:
        inside += ' ' + ' '.join((f'{key}="{value}"' for key, value in tag.attributes.items()))
    if tag.text:
        out.write(f'<{inside}>')
    else:
        out.write(f'<{inside}/>')


def dump(root: XML_Tag, out: io.StringIO):
    dump_tag(root, out)
    if root.text:
        out.write(root.text[0])
        for nchild, child in enumerate(root.children):
            dump(child, out)
            if nchild + 1 < len(root.text):
                out.write(root.text[nchild + 1])
        out.write(f'</{root.name}>')


def dump_document(document: XML_Document, out: io.StringIO):
    dump(document.root, out)
