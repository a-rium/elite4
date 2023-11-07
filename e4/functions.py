from __future__ import annotations

from ..e4 import XML_Element, XML_Fragment, XML_FragmentType

from typing import Callable


def append_child(parent: XML_Element, child: XML_Element):
    insert_child(parent, len(parent.fragments), child)


def insert_child(parent: XML_Element, index: int, child: XML_Element):
    parent.fragments.insert(index, XML_Fragment(kind=XML_FragmentType.ELEMENT, data=child))


def append_text(parent: XML_Element, text: str):
    insert_text(parent, len(parent.fragments), text)


def insert_text(parent: XML_Element, index: int, text: str):
    parent.fragments.insert(index, XML_Fragment(kind=XML_FragmentType.CHAR_DATA, data=text))


def find_first(node: XML_Element, condition: Callable[[XML_Fragment], bool]) -> XML_Fragment:
    first, _ = find_first_with_index(node, condition)
    return first


def find_first_with_index(node: XML_Element, condition: Callable[[XML_Fragment], bool]) -> tuple[XML_Fragment, int]:
    for index, fragment in enumerate(node.fragments):
        if condition(fragment):
            return fragment, index
