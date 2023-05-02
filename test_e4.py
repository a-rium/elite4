from e4 import parse


def test_single_element():
    data = parse('<element > body </element >')
    assert data.name == 'element'
    assert len(data.children) == 0
    # TODO body must start and end with non-whitespace character
    assert data.text == ' body '
