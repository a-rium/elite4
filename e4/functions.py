from __future__ import annotations

from ..e4 import XML_Tag, XML_Fragment, XML_FragmentType

from typing import Callable


def append_child(parent: XML_Tag, child: XML_Tag):
    insert_child(parent, len(parent.fragments), child)


def insert_child(parent: XML_Tag, index: int, child: XML_Tag):
    parent.fragments.insert(index, XML_Fragment(kind=XML_FragmentType.ELEMENT, data=child))


def append_text(parent: XML_Tag, text: str):
    insert_text(parent, len(parent.fragments), text)


def insert_text(parent: XML_Tag, index: int, text: str):
    parent.fragments.insert(index, XML_Fragment(kind=XML_FragmentType.CHAR_DATA, data=text))


def find_first(node: XML_Tag, condition: Callable[[XML_Fragment], bool]) -> XML_Fragment:
    first, _ = find_first_with_index(node, condition)
    return first


def find_first_with_index(node: XML_Tag, condition: Callable[[XML_Fragment], bool]) -> tuple[XML_Fragment, int]:
    for index, fragment in enumerate(node.fragments):
        if condition(fragment):
            return fragment, index