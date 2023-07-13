from e4 import parse


def assert_element(element, /, name, nchildren, attributes, namespaces, text):
    assert element.name == name
    assert len(element.children) == nchildren
    assert element.attributes == attributes
    assert element.namespaces == namespaces
    assert element.text.strip() == text


def test_empty_element():
    element = parse('<element></element>')
    assert_element(element.root,
                   name='element',
                   nchildren=0,
                   attributes={},
                   namespaces={},
                   text='')


def test_single_element():
    element = parse('<element > body </element >')
    assert_element(element.root,
                   name='element',
                   nchildren=0,
                   attributes={},
                   namespaces={},
                   text='body')


def test_attributes():
    element = parse('<element kind="string" >Body</element>')
    assert_element(element.root,
                   name='element',
                   nchildren=0,
                   attributes={'kind': 'string'},
                   namespaces={},
                   text='Body')


def test_nondefault_namespace():
    element = parse('<my:element xmlns:my="http://my.namespace.org" my:kind = "string">Body</my:element >')
    assert_element(element.root,
                   name='my:element',
                   nchildren=0,
                   attributes={'my:kind': 'string'},
                   namespaces={'xmlns:my': 'http://my.namespace.org'},
                   text='Body')


def test_nested_namespace():
    element = parse('<my:other:element xmlns:my:other="http://my.namespace.org" my:other:kind = "string">Body</my:other:element >')
    assert_element(element.root,
                   name='my:other:element',
                   nchildren=0,
                   attributes={'my:other:kind': 'string'},
                   namespaces={'xmlns:my:other': 'http://my.namespace.org'},
                   text='Body')


def test_element_with_dashes():
    element = parse('<special-element>Special!</special-element>')
    assert_element(element.root,
                   name='special-element',
                   nchildren=0,
                   attributes={},
                   namespaces={},
                   text='Special!')


def test_attribute_with_dashes():
    element = parse('<element element-status="normal">Normal!</element>')
    assert_element(element.root,
                   name='element',
                   nchildren=0,
                   attributes={'element-status': 'normal'},
                   namespaces={},
                   text='Normal!')


def test_element_with_periods():
    element = parse('<special.element>Special!</special.element>')
    assert_element(element.root,
                   name='special.element',
                   nchildren=0,
                   attributes={},
                   namespaces={},
                   text='Special!')


def test_attribute_with_periods():
    element = parse('<element element.status="normal">Normal!</element>')
    assert_element(element.root,
                   name='element',
                   nchildren=0,
                   attributes={'element.status': 'normal'},
                   namespaces={},
                   text='Normal!')


def test_sub_elements():
    element = parse('<element xmlns="http://my.default.namespace.org" kind="string" xmlns:sub2="http://sub2.namespace.org"><sub-element.text>Body</sub-element.text><sub2:sub-element.text sub2:source="testfile">Second Body</sub2:sub-element.text></element>')
    assert_element(element.root,
                   name='element',
                   nchildren=2,
                   attributes={'kind': 'string'},
                   namespaces={'xmlns': 'http://my.default.namespace.org', 'xmlns:sub2': 'http://sub2.namespace.org'},
                   text='')
    subelement = element.root.children[0]
    assert_element(subelement,
                   name='sub-element.text',
                   nchildren=0,
                   attributes={},
                   namespaces={},
                   text='Body')
    subelement2 = element.root.children[1]
    assert_element(subelement2,
                   name='sub2:sub-element.text',
                   nchildren=0,
                   attributes={'sub2:source': 'testfile'},
                   namespaces={},
                   text='Second Body')


# def test_failure_mismatching_tags_no_space():
#     with pytest.raises(BadFormat):
#         parse('<element> </other>')
#
#
# def test_failure_mismatching_tags_space():
#     with pytest.raises(BadFormat):
#         parse('<element> </other >')
