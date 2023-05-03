from e4 import parse


def test_single_element():
    element = parse('<element > body </element >')
    assert element.name == 'element'
    assert len(element.children) == 0
    assert len(element.attributes) == 0
    # TODO body must start and end with non-whitespace character
    assert element.text == ' body '


def test_attributes():
    element = parse('<element kind="string" >Body</element>')
    assert element.name == 'element'
    assert len(element.children) == 0
    assert len(element.attributes) == 1
    assert 'kind' in element.attributes
    assert element.attributes['kind'] == 'string'
    assert element.text == 'Body'


def test_nondefault_namespace():
    element = parse('<my:element xmlns:xs="http://my.namespace.org" my:kind = "string">Body</my:namespace >')
    assert element.name == 'my:element'
    assert len(element.children) == 0
    assert len(element.attributes) == 2
    assert element.text == 'Body'


def test_sub_elements():
    element = parse('<element xmlns="http://my.default.namespace.org" kind="string" xmlns:sub2="http://sub2.namespace.org"><subelement>Body</subelement><sub2:subelement sub2:source="testfile">Second Body</sub2:subelement></element>')
    assert element.name == 'element'
    assert len(element.children) == 2
    assert len(element.attributes) == 3
    assert element.text == ''
    subelement = element.children[0]
    assert subelement.name == 'subelement'
    assert len(subelement.children) == 0
    assert len(subelement.attributes) == 0
    assert subelement.text == 'Body'
    subelement2 = element.children[1]
    assert subelement2.name == 'sub2:subelement'
    assert len(subelement2.children) == 0
    assert len(subelement2.attributes) == 1
    assert 'sub2:source' in subelement2.attributes
    assert subelement2.attributes['sub2:source'] == 'testfile'
    assert subelement2.text == 'Second Body'
