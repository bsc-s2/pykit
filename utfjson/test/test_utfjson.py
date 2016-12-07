#!/usr/bin/env python2.6
# coding: utf-8

import unittest

import utfjson


class TestUTFJson(unittest.TestCase):

    def test_load(self):

        self.assertEqual(None, utfjson.load(None))

        self.assertEqual({}, utfjson.load('{}'))
        self.assertEqual('我'.decode('utf-8'), utfjson.load('"\\u6211"'))

    def test_dump(self):
        self.assertEqual('null', utfjson.dump(None))
        self.assertEqual('{}', utfjson.dump({}))
        self.assertEqual('"\\u6211"', utfjson.dump('我'))
