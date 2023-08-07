from e4 import parse, parse_xml_declaration


def assert_element(element, /, name, nchildren, attributes, text):
    assert element.name == name
    assert len(element.children) == nchildren
    assert element.attributes == attributes
    # Todo(Correctness) test for fragments instead of joining and stripping
    assert ''.join(element.text).strip() == text



def test_empty_element():
    element = parse('<element></element>')
    assert_element(element.root,
                   name='element',
                   nchildren=0,
                   attributes={},
                   text='')


def test_single_element():
    element = parse('<element > body </element >')
    assert_element(element.root,
                   name='element',
                   nchildren=0,
                   attributes={},
                   text='body')


def test_attributes():
    element = parse('<element kind="string" >Body</element>')
    assert_element(element.root,
                   name='element',
                   nchildren=0,
                   attributes={'kind': 'string'},
                   text='Body')


def test_nondefault_namespace():
    element = parse('<my:element xmlns:my="http://my.namespace.org" my:kind = "string">Body</my:element >')
    assert_element(element.root,
                   name='my:element',
                   nchildren=0,
                   attributes={'my:kind': 'string', 'xmlns:my': 'http://my.namespace.org'},
                   text='Body')


def test_nested_namespace():
    element = parse('<my:other:element xmlns:my:other="http://my.namespace.org" my:other:kind = "string">Body</my:other:element >')
    assert_element(element.root,
                   name='my:other:element',
                   nchildren=0,
                   attributes={'my:other:kind': 'string', 'xmlns:my:other': 'http://my.namespace.org'},
                   text='Body')


def test_element_with_dashes():
    element = parse('<special-element>Special!</special-element>')
    assert_element(element.root,
                   name='special-element',
                   nchildren=0,
                   attributes={},
                   text='Special!')


def test_attribute_with_dashes():
    element = parse('<element element-status="normal">Normal!</element>')
    assert_element(element.root,
                   name='element',
                   nchildren=0,
                   attributes={'element-status': 'normal'},
                   text='Normal!')


def test_element_with_periods():
    element = parse('<special.element>Special!</special.element>')
    assert_element(element.root,
                   name='special.element',
                   nchildren=0,
                   attributes={},
                   text='Special!')


def test_attribute_with_periods():
    element = parse('<element element.status="normal">Normal!</element>')
    assert_element(element.root,
                   name='element',
                   nchildren=0,
                   attributes={'element.status': 'normal'},
                   text='Normal!')


def test_sub_elements():
    element = parse('<element xmlns="http://my.default.namespace.org" kind="string" xmlns:sub2="http://sub2.namespace.org"><sub-element.text>Body</sub-element.text><sub2:sub-element.text sub2:source="testfile">Second Body</sub2:sub-element.text></element>')
    assert_element(element.root,
                   name='element',
                   nchildren=2,
                   attributes={'kind': 'string', 'xmlns': 'http://my.default.namespace.org', 'xmlns:sub2': 'http://sub2.namespace.org'},
                   text='')
    subelement = element.root.children[0]
    assert_element(subelement,
                   name='sub-element.text',
                   nchildren=0,
                   attributes={},
                   text='Body')
    subelement2 = element.root.children[1]
    assert_element(subelement2,
                   name='sub2:sub-element.text',
                   nchildren=0,
                   attributes={'sub2:source': 'testfile'},
                   text='Second Body')


def test_parse_document_with_xml_declaration():
    document = parse('<?xml version="1.0" ?><element property="a"> abcd </element>')
    assert document.declaration.version == '1.0'
    assert_element(document.root,
                   name='element',
                   nchildren=0,
                   attributes={'property': 'a'},
                   text='abcd')


def test_parse_xml_declaration_with_encoding():
    declaration, _, ok = parse_xml_declaration('<?xml version="1.0" encoding="utf-8"?>', 0)
    assert ok
    assert declaration.version == '1.0'
    assert declaration.encoding == 'utf-8'


def test_parse_xml_declaration_with_standalone_no():
    declaration, _, ok = parse_xml_declaration('<?xml version="1.0" standalone="no"?>', 0)
    assert ok
    assert declaration.version == '1.0'
    assert not declaration.standalone


def test_parse_xml_declaration_with_standalone_yes():
    declaration, _, ok = parse_xml_declaration('<?xml version="1.0" standalone="yes"?>', 0)
    assert ok
    assert declaration.version == '1.0'
    assert declaration.standalone


def test_parse_full_xml_declaration():
    declaration, _, ok = parse_xml_declaration('<?xml version="1.0" encoding="utf-16" standalone="yes"?>', 0)
    assert ok
    assert declaration.version == '1.0'
    assert declaration.encoding == 'utf-16'
    assert declaration.standalone

# def test_failure_mismatching_tags_no_space():
#     with pytest.raises(BadFormat):
#         parse('<element> </other>')
#
#
# def test_failure_mismatching_tags_space():
#     with pytest.raises(BadFormat):
#         parse('<element> </other >')
