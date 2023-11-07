from __future__ import annotations

from ..e4 import Element, Fragment, FragmentType

from typing import Callable


def append_child(parent: Element, child: Element):
    insert_child(parent, len(parent.fragments), child)


def insert_child(parent: Element, index: int, child: Element):
    parent.fragments.insert(index, Fragment(kind=FragmentType.ELEMENT, data=child))


def append_text(parent: Element, text: str):
    insert_text(parent, len(parent.fragments), text)


def insert_text(parent: Element, index: int, text: str):
    parent.fragments.insert(index, Fragment(kind=FragmentType.CHAR_DATA, data=text))


def find_first(node: Element, condition: Callable[[Fragment], bool]) -> Fragment:
    first, _ = find_first_with_index(node, condition)
    return first


def find_first_with_index(node: Element, condition: Callable[[Fragment], bool]) -> tuple[Fragment, int]:
    for index, fragment in enumerate(node.fragments):
        if condition(fragment):
            return fragment, index
