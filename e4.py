from __future__ import annotations
from toke import Token, TokenKind
from enum import Enum

import toke
import dataclasses


@dataclasses.dataclass
class XML_Tag:
    name: str
    attributes: dict[str, str]
    namespaces: dict[str, str]
    text: str
    children: list[XML_Tag]
    parent: XML_Tag
    _current_attribute: str

    def __init__(self, parent):
        self.name = ''
        self.attributes = {}
        self.namespaces = {}
        self.text = ''
        self.children = []
        self.parent = parent
        self._current_attribute = ''


class State(Enum):
    START = 0
    START_ELEMENT = 1
    AFTER_ELEMENT_NAME = 2
    NAMESPACE_ELEMENT = 3
    START_ATTRIBUTE = 4
    ATTRIBUTE_NAME = 5
    EXPECTING_ATTRIBUTE_ASSIGNMENT = 6
    ATTRIBUTE_VALUE = 7
    END_ATTRIBUTE = 8
    BODY = 9
    INNER_ELEMENT = 10
    EXPECTING_CLOSING_ELEMENT = 11
    EXPECTING_END_ELEMENT = 12
    END_ELEMENT = 13


def panic():
    print('Panic!')
    exit(1)


def action_start(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 0
    while tokens[at + length].kind != TokenKind.PUNCTUATION or tokens[at].text != '<':
        length += 1

    child = XML_Tag(tag)
    tag.children.append(child)

    return State.START_ELEMENT, at + length + 1, child


def action_start_element(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 0
    if tokens[at].kind == TokenKind.SPACE:
        length += 1

    if tokens[at + length].kind == TokenKind.WORD:
        tag.name += tokens[at + length].text
        return State.AFTER_ELEMENT_NAME, at + length + 1, tag

    panic()


def action_after_element_name(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 1
    if tokens[at].kind == TokenKind.PUNCTUATION and tokens[at].text == ':':
        tag.name += tokens[at].text
        return State.NAMESPACE_ELEMENT, at + length, tag
    elif tokens[at].kind == TokenKind.SPACE:
        return State.START_ATTRIBUTE, at + length, tag
    elif tokens[at].kind == TokenKind.PUNCTUATION and tokens[at].text == '>':
        return State.BODY, at + length, tag

    panic()


def action_namespace_element(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 1
    if tokens[at].kind == TokenKind.WORD:
        tag.name += tokens[at].text
        return State.AFTER_ELEMENT_NAME, at + length, tag

    panic()


def action_start_attribute(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 1
    if tokens[at].kind == TokenKind.WORD:
        tag._current_attribute += tokens[at].text
        return State.ATTRIBUTE_NAME, at + length, tag
    elif tokens[at].kind == TokenKind.PUNCTUATION and tokens[at].text == '>':
        return State.BODY, at + length, tag

    panic()


def action_attribute_name(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 1
    if tokens[at].kind == TokenKind.PUNCTUATION and tokens[at].text == ':':
        tag._current_attribute += tokens[at].text
        return State.START_ATTRIBUTE, at + length, tag
    elif tokens[at].kind == TokenKind.SPACE:
        return State.EXPECTING_ATTRIBUTE_ASSIGNMENT, at + length, tag
    elif tokens[at].kind == TokenKind.PUNCTUATION and tokens[at].text == '=':
        return State.ATTRIBUTE_VALUE, at + length, tag

    panic()


def action_expecting_attribute_assignment(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 1
    if tokens[at].kind == TokenKind.PUNCTUATION and tokens[at].text == '=':
        return State.ATTRIBUTE_VALUE, at + length, tag

    panic()


def action_attribute_value(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 1
    if tokens[at].kind == TokenKind.QUOTATION:
        tag.attributes[tag._current_attribute] = tokens[at].text[1:-1]
        tag._current_attribute = ''
        return State.END_ATTRIBUTE, at + length, tag

    panic()


def action_end_attribute(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 1
    if tokens[at].kind == TokenKind.SPACE:
        return State.START_ATTRIBUTE, at + length, tag
    elif tokens[at].kind == TokenKind.PUNCTUATION and tokens[at].text == '>':
        return State.BODY, at + length, tag

    panic()


def action_body(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 0
    while tokens[at + length].kind != TokenKind.PUNCTUATION or tokens[at + length].text != '<':
        tag.text += tokens[at + length].text
        length += 1

    return State.INNER_ELEMENT, at + length + 1, tag


def action_inner_element(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 1
    if tokens[at].kind == TokenKind.PUNCTUATION and tokens[at].text == '/':
        return State.EXPECTING_CLOSING_ELEMENT, at + length, tag
    elif tokens[at].kind == TokenKind.SPACE or tokens[at].kind == TokenKind.WORD:
        child = XML_Tag(tag)
        tag.children.append(child)
        return State.START_ELEMENT, at, child

    panic()


def action_expecting_closing_element(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 1
    if tokens[at].kind == TokenKind.WORD:
        return State.EXPECTING_END_ELEMENT, at + length, tag

    panic()


def action_expecting_end_element(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 1
    if tokens[at].kind == TokenKind.PUNCTUATION and tokens[at].text == '>':
        # TODO assert that closing tag is the same as the opening one
        return State.BODY, at + length, tag.parent
    elif tokens[at].kind == TokenKind.PUNCTUATION and tokens[at].text == ':':
        return State.EXPECTING_CLOSING_ELEMENT, at + length, tag
    elif tokens[at].kind == TokenKind.SPACE:
        return State.END_ELEMENT, at + length, tag

    panic()


def action_end_element(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 1
    if tokens[at].kind == TokenKind.PUNCTUATION and tokens[at].text == '>':
        # TODO assert that closing tag is the same as the opening one
        return State.BODY, at + length, tag.parent

    panic()


ACTIONS = (action_start,
           action_start_element,
           action_after_element_name,
           action_namespace_element,
           action_start_attribute,
           action_attribute_name,
           action_expecting_attribute_assignment,
           action_attribute_value,
           action_end_attribute,
           action_body,
           action_inner_element,
           action_expecting_closing_element,
           action_expecting_end_element,
           action_end_element)


def parse(xml: str) -> XML_Tag:
    tokens = toke.parse_tokens(xml)
    at = 0
    state = State.START
    tag = XML_Tag(None)
    while at < len(tokens):
        state, at, tag = ACTIONS[state.value](tokens, at, tag)
    return tag.children[0]


def main() -> int:
    parse('<ws:notification type="urgent" ws:priority="1"> abcd<example></example>efgh </ws:notification>')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
