from __future__ import annotations
from typing import Union

import dataclasses
import string
import enum


class FragmentType(enum.Enum):
    ELEMENT = enum.auto()
    CHAR_DATA = enum.auto()
    ENTITY_REFERENCE = enum.auto()
    CHAR_REFERENCE = enum.auto()


@dataclasses.dataclass
class Fragment:
    kind: FragmentType
    data: Union[str, Element]


@dataclasses.dataclass
class Attribute:
    key: str
    value: str


@dataclasses.dataclass
class Declaration:
    version: str
    encoding: str
    standalone: bool


class Document:
    def __init__(self, declaration: Declaration, root: Element):
        self.declaration = declaration
        self.root = root


class Element:
    name: str
    attributes: dict[str, str]
    fragments: list[Fragment]
    parent: Element

    def __init__(self, *, name: str = '', attributes: dict[str, str] = None, fragments: list[Element] = None, parent=None):
        self.name = name
        self.attributes = attributes if attributes is not None else dict()
        self.fragments = fragments if fragments is not None else []
        self.parent = parent

    @property
    def children(self):
        return [fragment.data for fragment in self.fragments if fragment.kind == FragmentType.ELEMENT]

    @property
    def text(self):
        return [fragment.data for fragment in self.fragments if fragment.kind in {FragmentType.CHAR_DATA, FragmentType.CHAR_REFERENCE, FragmentType.ENTITY_REFERENCE}]


def normalize_end_of_line(content: str) -> str:
    at = 0
    normalized = ''
    while at < len(content):
        if content[at] in {'\x85', '\u2028'}:
            normalized += '\x0A'
        elif content[at] == '\x0D':
            if at + 1 < len(content) and content[at + 1] in {'\x0A', '\x85'}:
                at += 1
            normalized += '\x0A'
        else:
            normalized += content[at]
        at += 1
    return normalized


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


# See https://www.w3.org/TR/xml/#NT-EntityRef
def parse_entity_reference(text: str, at: int) -> tuple[str, int, bool]:
    current = at
    ok = False
    if text[current] == '&':
        current += 1
        entity_name, current, parsed = parse_name(text, current)
        if parsed and text[current] == ';':
            current += 1
            ok = True
    return text[at:current], current, ok


# See https://www.w3.org/TR/xml/#NT-CharRef
def parse_char_reference(text: str, at: int) -> tuple[str, int, bool]:
    current = at
    ok = False
    if current + 1 < len(text) and text[current:current + 2] == '&#':
        current += 2
        allowed_chars = string.digits
        if text[current] == 'x':
            current += 1
            allowed_chars += 'abcdefABCDEF'

        parsed = False
        while current < len(text) - 1 and text[current] in allowed_chars:
            current += 1
            parsed = True

        if parsed and text[current] == ';':
            current += 1
            ok = True

    return text[at:current], current, ok


# See https://www.w3.org/TR/xml/#NT-Reference
def parse_reference(text: str, at: int) -> tuple[str, int, bool, FragmentType]:
    current = at
    ok = False
    kind = FragmentType.CHAR_REFERENCE
    reference, new_current, parsed = parse_char_reference(text, current)
    if not parsed:
        kind = FragmentType.ENTITY_REFERENCE
        reference, new_current, parsed = parse_entity_reference(text, current)

    ok = parsed
    current = new_current
    return reference, current, ok, kind


# See https://www.w3.org/TR/xml/#NT-Name
# TODO(Compliance):  add support for spec-allowed Unicode encoded characters
def parse_name(text: str, at: int) -> tuple[str, int, bool]:
    allowed_first_chars = f':_{string.ascii_letters}'
    allowed_non_first_chars = f'{allowed_first_chars}{string.digits}-.'

    current = at
    ok = text[current] in allowed_first_chars
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
def parse_start_tag(text: str, at: int, parent: Element) -> tuple[Element, bool, int, bool]:
    element = None

    current = at
    ok = False
    empty_element = False
    if text[current] == '<':
        current += 1
        element_name, current, parsed = parse_name(text, current)
        attributes: dict[str, str] = {}
        if parsed:
            while True:
                _, current, parsed = parse_white_space(text, current)
                if not parsed:
                    break
                attribute, current, parsed = parse_attribute(text, current)
                if not parsed:
                    break

                # TODO(Compliance): verify that the attribute/namespace has not been already added
                attributes[attribute.key] = attribute.value

            _, current, _ = parse_white_space(text, current)
            empty_element = text[current] == '/'
            if empty_element:
                current += 1
            ok = text[current] == '>'
            if ok:
                current += 1
                element = Element(parent=parent)
                element.name = element_name
                element.attributes = attributes

    return element, empty_element, current, ok


# See https://www.w3.org/TR/xml/#NT-current
def parse_content(text: str, at: int, current_element: Element, _recursive_call=False) -> tuple[int, bool]:
    current = at
    ok = True

    while True:
        data, current, parsed = parse_char_data(text, current)
        if not parsed:
            ok = False
            break

        normalized_data = normalize_end_of_line(data)
        if len(normalized_data) > 0:
            current_element.fragments.append(Fragment(kind=FragmentType.CHAR_DATA, data=normalized_data))
        else:
            child, new_current, parsed = parse_element(text, current, current_element)
            if parsed:
                current = new_current
                current_element.fragments.append(Fragment(kind=FragmentType.ELEMENT, data=child))
            else:
                entity, new_current, parsed, kind = parse_reference(text, current)
                if parsed:
                    current = new_current
                    current_element.fragments.append(Fragment(kind=kind, data=entity))
                    # TODO(Compliance): add support for CDSects, PIs and Comments

        # TODO(Improvement): is the forward lookup required?
        if current + 1 < len(text) and text[current:current + 2] == '</':
            break
    return current, ok


# See https://www.w3.org/TR/xml/#NT-ETag
def parse_end_tag(text: str, at: int, current_element: Element) -> tuple[int, bool]:
    current = at
    ok = current + 1 < len(text) and text[current:current + 2] == '</'
    if ok:
        current += 2
        element_name, current, ok = parse_name(text, current)
        ok = True if ok and current_element.name == element_name else False
        if ok:
            _, current, _ = parse_white_space(text, current)
            ok = text[current] == '>'
            if ok:
                current += 1
    return current, ok


# See https://www.w3.org/TR/xml/#NT-element
def parse_element(text: str, at: int, parent: Element) -> [Element, int, bool]:
    current = at

    element, empty_element, current, ok = parse_start_tag(text, current, parent)
    if ok and not empty_element:
        current, ok = parse_content(text, current, element)
        if ok:
            current, ok = parse_end_tag(text, current, element)

    return element, current, ok


# See https://www.w3.org/TR/xml/#NT-XMLDecl
def parse_xml_declaration(text: str, at: int) -> tuple[Declaration, int, bool]:
    declaration: Declaration = None
    current = at
    ok = True

    if text[current:current + 5] == '<?xml':
        ok = False
        current += 5
        _, current, parsed = parse_white_space(text, current)
        if parsed:
            attribute, current, parsed = parse_attribute(text, current)
            if parsed and attribute.key == 'version':
                # Todo(Compliance): validate version value according to spec.
                version = attribute.value
                _, current, ok = parse_white_space(text, current)
                if ok:

                    # Todo(Compliance): in case the standalone attribute is not declared,
                    # - if an external entity reference is found, then it is assumed as false
                    # - otherwise it is assumed as true
                    standalone = None
                    encoding = None

                    attribute, current, parsed = parse_attribute(text, current)
                    if parsed and attribute.key == 'encoding':
                        encoding = attribute.value
                        _, current, ok = parse_white_space(text, current)
                        attribute, current, parsed = parse_attribute(text, current)
                    if parsed and attribute.key == 'standalone' and attribute.value in {'yes', 'no'}:
                        standalone = True if attribute.value == 'yes' else False
                    _, current, _ = parse_white_space(text, current)
                    ok = text[current:current + 2] == '?>'
                    if ok:
                        current += 2
                        declaration = Declaration(version=version, encoding=encoding, standalone=standalone)

    return declaration, current, ok


# See https://www.w3.org/TR/xml/#NT-document
# TODO(Compliance): add support for prolog and Misc
def parse_document(text: str, at=0) -> tuple[Document, int, bool]:
    document = None

    current = at
    # Todo(Compliance) parse prolog instead
    declaration, current, ok = parse_xml_declaration(text, current)
    _, current, _ = parse_white_space(text, current)
    root, current, ok = parse_element(text, current, None)
    if ok:
        document = Document(declaration, root)
    return document, current, ok


def parse(xml: str) -> Document:
    document, _, _ = parse_document(xml)
    return document
