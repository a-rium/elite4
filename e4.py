from __future__ import annotations

import dataclasses
import io
import string
import itertools


@dataclasses.dataclass
class Attribute:
    key: str
    value: str


# See https://www.w3.org/TR/xml/#NT-S
def parse_white_space(text: str, at: int) -> tuple[str, int, bool]:
    allowed_chars = '\x20\x09\x0D\x0A'

    current = at
    ok = False
    while current < len(text):
        if text[current] not in allowed_chars:
            break
        current += 1
        ok = True
    return text[at:current], current, ok


# See https://www.w3.org/TR/xml/#NT-CharData
def parse_char_data(text: str, at: int) -> tuple[str, int, bool]:
    not_allowed_chars = '<&'

    current = at
    ok = True
    while current < len(text):
        if current + 2 < len(text) and text[current + 3] == ']]>':
            ok = False
            break
        if text[current] in not_allowed_chars:
            break
        current += 1

    return text[at:current], current, ok


# See https://www.w3.org/TR/xml/#NT-Name
# TODO(Compliance):  add support for spec-allowed Unicode encoded characters
# TODO(Performance): turn allowed chars list into strings
def parse_name(text: str, at: int) -> tuple[str, int, bool]:
    allowed_first_chars = [':', '_', *list(string.ascii_letters)]
    allowed_non_first_chars = [':', '_', *list(string.ascii_letters), *list(string.digits), '-', '.']

    current = at
    ok = text[at] in allowed_first_chars
    if ok:
        current = at + 1
        while current < len(text):
            if text[current] not in allowed_non_first_chars:
                break
            current += 1
    return text[at:current], current, ok


# See https://www.w3.org/TR/xml/#NT-AttValue
# TODO(Compliance): add support for References
def parse_attribute_value(text: str, at: int) -> tuple[str, int, bool]:
    current = at
    ok = False
    quote = text[at]
    if quote in ['"', "'"]:
        not_allowed_chars = f'<&{quote}'

        current += 1
        while current < len(text):
            if text[current] in not_allowed_chars:
                ok = text[current] == quote
                current += 1
                break
            current += 1
    return text[at:current], current, ok


# See https://www.w3.org/TR/xml/#NT-Attribute
def parse_attribute(text: str, at: int) -> tuple[Attribute, int, bool]:
    attribute: Attribute = None
    current = at
    ok = False

    key, current, parsed = parse_name(text, current)
    if parsed:
        _, current, _ = parse_white_space(text, current)
        if text[current] == '=':
            current += 1
            _, current, _ = parse_white_space(text, current)
            value, current, ok = parse_attribute_value(text, current)
            if ok:
                attribute = Attribute(key=key, value=value[1:-1])
    return attribute, current, ok


# See https://www.w3.org/TR/xml/#NT-STag
def parse_start_tag(text: str, at: int, parent: XML_Tag) -> tuple[XML_Tag, bool, int, bool]:
    tag = None

    current = at
    ok = False
    empty_tag = False
    if text[current] == '<':
        current += 1
        tagname, current, parsed = parse_name(text, current)
        attributes: dict[str, str] = {}
        namespaces: dict[str, str] = {}
        if parsed:
            while True:
                _, current, parsed = parse_white_space(text, current)
                if not parsed:
                    break
                attribute, current, parsed = parse_attribute(text, current)
                if not parsed:
                    break

                # TODO(Compliance): verify that the attribute/namespace has not been already added
                if attribute.key.startswith('xmlns'):
                    namespaces[attribute.key] = attribute.value
                else:
                    attributes[attribute.key] = attribute.value

            _, current, _ = parse_white_space(text, current)
            empty_tag = text[current] == '/'
            if empty_tag:
                current += 1
            ok = text[current] == '>'
            if ok:
                current += 1
                tag = XML_Tag(parent)
                tag.name = tagname
                tag.attributes = attributes
                tag.namespaces = namespaces

    return tag, empty_tag, current, ok


# See https://www.w3.org/TR/xml/#NT-current
def parse_content(text: str, at: int, current_tag: XML_Tag, _recursive_call=False) -> tuple[int, bool]:
    current = at
    ok = True

    # TODO(Compliance): element content should be normalized ex. whitespaces should be removed / deduplicated
    data, current, ok = parse_char_data(text, current)
    if ok:
        # TODO(Compliance): keep content segments separated
        current_tag.text += data
        while True:
            child, new_current, parsed = parse_element(text, current, current_tag)
            if parsed:
                current = new_current
                current_tag.children.append(child)
            else:
                # TODO(Compliance): add support for References, CDSects, PIs and Comments
                pass

            # TODO(Compliance): element content should be normalized ex. whitespaces should be removed / deduplicated
            data, current, ok = parse_char_data(text, current)
            # TODO(Compliance): keep content segments separated
            if not ok:
                break
            # TODO(Improvement): is the forward lookup required?
            if current + 1 < len(text) and text[current:current + 2] == '</':
                break
    return current, ok


# See https://www.w3.org/TR/xml/#NT-ETag
def parse_end_tag(text: str, at: int, current_tag: XML_Tag) -> tuple[int, bool]:
    current = at
    ok = current + 1 < len(text) and text[current:current + 2] == '</'
    if ok:
        current += 2
        tagname, current, ok = parse_name(text, current)
        ok = True if ok and current_tag.name == tagname else False
        if ok:
            _, current, _ = parse_white_space(text, current)
            ok = text[current] == '>'
            if ok:
                current += 1
    return current, ok


# See https://www.w3.org/TR/xml/#NT-element
def parse_element(text: str, at: int, parent: XML_Tag) -> [XML_Tag, int, bool]:
    current = at

    element, empty_tag, current, ok = parse_start_tag(text, current, parent)
    if ok and not empty_tag:
        current, ok = parse_content(text, current, element)
        if ok:
            current, ok = parse_end_tag(text, current, element)

    return element, current, ok


# See https://www.w3.org/TR/xml/#NT-document
# TODO(Compliance): add support for prolog and Misc
def parse_document(text: str, at=0) -> tuple[XML_Document, int, bool]:
    document = None

    current = at
    root, current, ok = parse_element(text, current, None)
    if ok:
        document = XML_Document(root)
    return document, current, ok


# raise XMLSyntaxException(f'expected tag name while parsing start-tag, got: {tagname}')

class XML_Document:
    def __init__(self, root: XML_Tag):
        self.root = root


@dataclasses.dataclass
class XML_Tag:
    name: str
    attributes: dict[str, str]
    namespaces: dict[str, str]
    text: str
    children: list[XML_Tag]
    parent: XML_Tag

    def __init__(self, parent):
        self.name = ''
        self.attributes = {}
        self.namespaces = {}
        self.text = ''
        self.children = []
        self.parent = parent


def parse(xml: str) -> XML_Document:
    document, _, _ = parse_document(xml)
    return document


def dump_tag(tag: XML_Tag, out: io.StringIO, nindentation: int, indentation: str):
    inside = tag.name
    if tag.attributes or tag.namespaces:
        inside += ' ' + ' '.join((f'{key}="{value}"' for key, value in itertools.chain(tag.attributes.items(), tag.namespaces.items())))
    out.write(f'{indentation * nindentation}<{inside}>')


def dump(root: XML_Tag, out: io.StringIO, /, newline, indentation, nindentation):
    dump_tag(root, out, nindentation, indentation)
    if newline:
        out.write('\n')
    if root.text:
        out.write((indentation * (nindentation + 1)) + root.text)
        if newline:
            out.write('\n')
    if root.children:
        for child in root.children:
            dump(child, out, nindentation=nindentation + 1, indentation=indentation, newline=newline)
            if newline:
                out.write('\n')
    out.write(f'{indentation * nindentation}</{root.name}>')


def dump_document(document: XML_Document, out: io.StringIO, /, newline=True, indentation='\t', nindentation=0):
    dump(document.root, out, newline=newline, indentation=indentation, nindentation=nindentation)
