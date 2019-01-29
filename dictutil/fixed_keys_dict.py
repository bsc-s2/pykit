#!/bin/env python2
# coding: utf-8


class FixedKeysDict(dict):

    # {'key', value_constructor}
    keys_default = {}

    # ordered keys as ident
    ident_keys = ()

    def __init__(self, *args, **argkv):

        super(FixedKeysDict, self).__init__(*args, **argkv)

        # Convert present keys
        for k in self:
            self[k] = self.keys_default[k](self[k])

        # Add default value to absent keys
        for k in self.keys_default:
            if k not in self:
                self[k] = self.keys_default[k]()

    def __setitem__(self, key, value):

        try:
            value = self.keys_default[key](value)
        except KeyError:
            raise KeyError('key: {key} is invalid'.format(key=key))
        except (ValueError, TypeError) as e:
            raise ValueError('value: {value} is invalid. {e}'.format(
                value=repr(value), e=repr(e)))

        super(FixedKeysDict, self).__setitem__(key, value)

    def ident(self):
        return tuple([self[k] for k in self.ident_keys])
