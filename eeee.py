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
    ZERO = 0
    ONE = 1
    TWO = 2
    TWOONE = 3
    THREE = 4
    FOUR = 5
    FIVE = 6
    SIX = 7
    SEVEN = 8
    EIGHT = 9
    NINE = 10
    TEN = 11
    ELEVEN = 12


def panic():
    print('Panic!')
    exit(1)


def action0(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 0
    while tokens[at + length].kind != TokenKind.PUNCTUATION or tokens[at].text != '<':
        length += 1

    child = XML_Tag(tag)
    tag.children.append(child)

    return State.ONE, at + length + 1, child


def action1(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 0
    if tokens[at].kind == TokenKind.SPACE:
        length += 1

    if tokens[at + length].kind == TokenKind.WORD:
        tag.name += tokens[at + length].text
        return State.TWO, at + length + 1, tag

    panic()


def action2(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 1
    if tokens[at].kind == TokenKind.PUNCTUATION and tokens[at].text == ':':
        tag.name += tokens[at].text
        return State.TWOONE, at + length, tag
    elif tokens[at].kind == TokenKind.SPACE:
        return State.THREE, at + length, tag
    elif tokens[at].kind == TokenKind.PUNCTUATION and tokens[at].text == '>':
        return State.EIGHT, at + length, tag

    panic()


def action21(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 1
    if tokens[at].kind == TokenKind.WORD:
        tag.name += tokens[at].text
        return State.TWO, at + length, tag

    panic()


def action3(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 1
    if tokens[at].kind == TokenKind.WORD:
        tag._current_attribute += tokens[at].text
        return State.FOUR, at + length, tag
    elif tokens[at].kind == TokenKind.PUNCTUATION and tokens[at].text == '>':
        return State.EIGHT, at + length, tag

    panic()


def action4(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 1
    if tokens[at].kind == TokenKind.PUNCTUATION and tokens[at].text == ':':
        tag._current_attribute += tokens[at].text
        return State.THREE, at + length, tag
    elif tokens[at].kind == TokenKind.SPACE:
        return State.FIVE, at + length, tag
    elif tokens[at].kind == TokenKind.PUNCTUATION and tokens[at].text == '=':
        return State.SIX, at + length, tag

    panic()


def action5(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 1
    if tokens[at].kind == TokenKind.PUNCTUATION and tokens[at].text == '=':
        return State.SIX, at + length, tag

    panic()


def action6(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 1
    if tokens[at].kind == TokenKind.QUOTATION:
        tag.attributes[tag._current_attribute] = tokens[at].text[1:-1]
        tag._current_attribute = ''
        return State.SEVEN, at + length, tag

    panic()


def action7(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 1
    if tokens[at].kind == TokenKind.SPACE:
        return State.THREE, at + length, tag
    elif tokens[at].kind == TokenKind.PUNCTUATION and tokens[at].text == '>':
        return State.EIGHT, at + length, tag

    panic()


def action8(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 0
    while tokens[at + length].kind != TokenKind.PUNCTUATION or tokens[at + length].text != '<':
        tag.text += tokens[at + length].text
        length += 1

    return State.NINE, at + length + 1, tag


def action9(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 1
    if tokens[at].kind == TokenKind.PUNCTUATION and tokens[at].text == '/':
        return State.TEN, at + length, tag
    elif tokens[at].kind == TokenKind.SPACE or tokens[at].kind == TokenKind.WORD:
        child = XML_Tag(tag)
        tag.children.append(child)
        return State.ONE, at, child

    panic()


def action10(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 1
    if tokens[at].kind == TokenKind.WORD:
        return State.ELEVEN, at + length, tag

    panic()


def action11(tokens: list[Token], at: int, tag: XML_Tag) -> tuple[State, int, XML_Tag]:
    length = 1
    if tokens[at].kind == TokenKind.PUNCTUATION and tokens[at].text == '>':
        # TODO assert that closing tag is the same as the opening one
        return State.EIGHT, at + length, tag.parent
    elif tokens[at].kind == TokenKind.PUNCTUATION and tokens[at].text == ':':
        return State.TEN, at + length, tag

    panic()


ACTIONS = (action0,
           action1,
           action2,
           action21,
           action3,
           action4,
           action5,
           action6,
           action7,
           action8,
           action9,
           action10,
           action11)


def parse(xml: str):
    tokens = toke.parse_tokens(xml)
    at = 0
    state = State.ZERO
    tag = XML_Tag(None)
    while at < len(tokens):
        state, at, tag = ACTIONS[state.value](tokens, at, tag)
        print(tag)


def main() -> int:
    parse('<ws:notification type="urgent" ws:priority="1"> abcd<example></example>efgh </ws:notification>')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
