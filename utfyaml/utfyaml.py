#! /usr/bin/env python2
# coding: utf-8

import re
import yaml

from yaml import MappingNode
from yaml import ScalarNode


def load(s, encoding='utf-8'):

    # override to set output encoding
    def construct_yaml_str(loader, node):
        value = loader.construct_scalar(node)

        if encoding is not None:
            return value.encode(encoding)

        return value

    yaml.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)

    return yaml.load(s)


def dump(s, encoding='utf-8', save_unicode=False):

    yaml.add_representer(str, represent_str)
    yaml.add_representer(dict, represent_mapping)

    # dump unicode as a str to remove '!!python/unicode' tag
    if not save_unicode:
        tag = u'tag:yaml.org,2002:str'
    else:
        tag = u'tag:yaml.org,2002:python/unicode'

    yaml.add_representer(unicode, lambda dumper,
                         data: dumper.represent_scalar(tag, data))

    if encoding is not None:
        dumped = yaml.dump(s, allow_unicode=True, encoding=encoding)

    else:
        dumped = yaml.dump(s, allow_unicode=True, encoding='utf-8')
        # unify encoding
        dumped = unicode(dumped, 'utf-8')

    # '...' is not necessary for yaml
    pattern = '\.\.\.\n$'

    return re.sub(pattern, '', dumped, 1)


def represent_str(dumper, data):

    # override to remove tag '!!python/str'
    tag = u'tag:yaml.org,2002:str'
    try:
        data = unicode(data, 'utf-8')
        style = None
    except UnicodeDecodeError:
        data = data.encode('base64')
        tag = u'tag:yaml.org,2002:binary'
        style = '|'

    return dumper.represent_scalar(tag, data, style=style)


def represent_mapping(dumper, mapping, flow_style=None):

    # override to dump map with item in any types
    value = []
    tag = u'tag:yaml.org,2002:map'
    node = MappingNode(tag, value, flow_style=flow_style)

    if dumper.alias_key is not None:
        dumper.represented_objects[dumper.alias_key] = node

    # there is the change
    # ex: [u'hello', '中国'].sort() raises an error

    # if hasattr(mapping, 'items'):
    #     mapping = mapping.items()
    #     mapping.sort()

    best_style = True
    for item_key, item_value in mapping.items():

        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        if not (isinstance(node_key, ScalarNode) and not node_key.style):
            best_style = False

        if not (isinstance(node_value, ScalarNode) and not node_value.style):
            best_style = False

        value.append((node_key, node_value))

    if flow_style is None:
        if dumper.default_flow_style is not None:
            node.flow_style = dumper.default_flow_style
        else:
            node.flow_style = best_style

    return node
