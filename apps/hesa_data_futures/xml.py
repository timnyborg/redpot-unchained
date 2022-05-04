from __future__ import annotations

import itertools
from collections import Counter
from urllib.request import urlopen

from lxml import etree

from django.conf import settings

from apps.hesa_data_futures import models


def save_xml(batch_id: int, tree: etree.Element) -> str:
    """Save the an xml tree to the protected media folder"""
    # create the media subfolder if required
    file_path = settings.PROTECTED_MEDIA_ROOT / 'hesa_data_futures'
    file_path.mkdir(parents=True, exist_ok=True)

    filename = f'conted_data_futures_batch_{batch_id}.xml'
    fullpath = file_path / filename
    with open(fullpath, 'w') as f:
        xml_string = etree.tostring(tree, pretty_print=True).decode('utf8')
        f.write(xml_string)
    return filename


def _model_to_node(model: models.XMLStagingModel) -> etree.Element:
    """Recursively convert an XMLStagingModel and its children into an xml tree"""
    node = etree.Element(model.element_name)
    # Fill with elements
    for column in model.xml_fields:
        value = getattr(model, column)
        if value is not None:
            etree.SubElement(node, column.upper()).text = str(value)

    # Create subnodes if any exist
    for child in itertools.chain.from_iterable(model.children()):
        node.append(_model_to_node(child))

    return node


def generate_tree(batch: models.Batch) -> etree.Element:
    """Serialize an entire batch as an XML tree"""
    return _model_to_node(batch)


def validate_xml(tree: etree.Element) -> dict[str, int]:
    """Validates the produced XML, and produces a dictionary of the errors: {description: count}"""

    # todo: using a hardcoded XSD url for 2022-23.  This will need to be dynamic in order to get the year's rules
    xsd_path = 'https://hesacodingmanualprod.blob.core.windows.net/strapi-files/assets/22056_1_3_0_103f2e1c86.xsd'

    # etree can only natively deal with http, so we get the XSD via urllib
    xmlschema_doc = etree.parse(urlopen(xsd_path))
    xmlschema = etree.XMLSchema(xmlschema_doc)

    try:
        xmlschema.assertValid(tree)
    except etree.DocumentInvalid as validation_error:
        return Counter(error.message for error in validation_error.error_log)
    return {}
