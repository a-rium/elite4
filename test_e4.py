from e4 import parse


def assert_element(element, /, name, nchildren, attributes, text):
    assert element.name == name
    assert len(element.children) == nchildren
    assert element.attributes == attributes
    assert element.text == text


def test_single_element():
    element = parse('<element > body </element >')
    # TODO body must start and end with non-whitespace character
    assert_element(element,
                   name='element',
                   nchildren=0,
                   attributes={},
                   text=' body ')


def test_attributes():
    element = parse('<element kind="string" >Body</element>')
    assert_element(element,
                   name='element',
                   nchildren=0,
                   attributes={'kind': 'string'},
                   text='Body')


def test_nondefault_namespace():
    element = parse('<my:element xmlns:xs="http://my.namespace.org" my:kind = "string">Body</my:namespace >')
    assert_element(element,
                   name='my:element',
                   nchildren=0,
                   attributes={'xmlns:xs': 'http://my.namespace.org', 'my:kind': 'string'},
                   text='Body')


def test_sub_elements():
    element = parse('<element xmlns="http://my.default.namespace.org" kind="string" xmlns:sub2="http://sub2.namespace.org"><subelement>Body</subelement><sub2:subelement sub2:source="testfile">Second Body</sub2:subelement></element>')
    assert_element(element,
                   name='element',
                   nchildren=2,
                   attributes={'xmlns': 'http://my.default.namespace.org', 'kind': 'string', 'xmlns:sub2': 'http://sub2.namespace.org'},
                   text='')
    subelement = element.children[0]
    assert_element(subelement,
                   name='subelement',
                   nchildren=0,
                   attributes={},
                   text='Body')
    subelement2 = element.children[1]
    assert_element(subelement2,
                   name='sub2:subelement',
                   nchildren=0,
                   attributes={'sub2:source': 'testfile'},
                   text='Second Body')
