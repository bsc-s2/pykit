#!/bin/env python2
# coding: utf-8

class FixedKeysDict(dict):

    # {'key', value_type}
    keys_default = {}

    # ordered keys as ident
    ident_keys = ()

    def __init__(self, *args, **argkv):

        for k in self.keys_default:
            self[k] = self.keys_default[k]()

        super(FixedKeysDict, self).__init__(*args, **argkv)

        # check self.keys() are valid or not
        for k in self:
            self[k] = self[k]

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
