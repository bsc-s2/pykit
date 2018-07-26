#!/usr/bin/env python3
# coding: utf-8

import unittest
from pykit.ectypes import referrer

ref1 = referrer.Referrer(Scope="3copy", RefKey="key1", Ver=123, IsDel=0)
ref2 = referrer.Referrer(Scope="2copy", RefKey="key1", Ver=123, IsDel=0)
ref3 = referrer.Referrer(Scope="3copy", RefKey="key2", Ver=123, IsDel=0)
ref4 = referrer.Referrer(Scope="3copy", RefKey="key1", Ver=124, IsDel=1)
ref5 = referrer.Referrer(Scope="3copy", RefKey="key1", Ver=123, IsDel=0)
ref6 = referrer.Referrer(Scope="3copy", RefKey="key1", Ver=1234, IsDel=0)
ref7 = referrer.Referrer(Scope="3copy", RefKey="key1", Ver=123, IsDel=1)
ref8 = referrer.Referrer(Scope="2copy", RefKey="key2", Ver=143, IsDel=0)
ref9 = referrer.Referrer(Scope="2copy", RefKey="key1", Ver=1234, IsDel=0)
ref10 = referrer.Referrer(Scope="2copy", RefKey="key1", Ver=124, IsDel=0)
ref11 = referrer.Referrer(Scope="2copy", RefKey="key2", Ver=123, IsDel=0)
ref12 = referrer.Referrer(Scope="2copy", RefKey="key2", Ver=124, IsDel=1)
ref13 = referrer.Referrer(Scope="3copy", RefKey="key12", Ver=123, IsDel=0)
ref14 = referrer.Referrer(Scope="3copy", RefKey="key1", Ver=12, IsDel=1)
ref15 = referrer.Referrer(Scope="3copy", RefKey="key2", Ver=12, IsDel=0)


class TestReferrer(unittest.TestCase):
    def test_eq(self):
        self.assertFalse(ref1.__eq__(ref2))
        self.assertFalse(ref1.__eq__(ref3))
        self.assertFalse(ref1.__eq__(ref4))
        self.assertTrue(ref1.__eq__(ref5))

    def test_ne(self):
        self.assertTrue(ref1.__ne__(ref6))
        self.assertTrue(ref6.__ne__(ref7))
        self.assertTrue(ref1.__ne__(ref8))
        self.assertFalse(ref1.__ne__(ref5))

    def test_ge(self):
        self.assertFalse(ref1.__ge__(ref3))
        self.assertFalse(ref1.__ge__(ref6))
        self.assertTrue(ref1.__ge__(ref9))
        self.assertTrue(ref5.__ge__(ref1))

    def test_gt(self):
        self.assertTrue(ref1.__gt__(ref2))
        self.assertFalse(ref1.__gt__(ref6))
        self.assertFalse(ref10.__gt__(ref1))
        self.assertFalse(ref5.__gt__(ref1))

    def test_le(self):
        self.assertTrue(ref1.__le__(ref7))
        self.assertFalse(ref1.__le__(ref11))
        self.assertFalse(ref1.__le__(ref12))
        self.assertTrue(ref5.__le__(ref1))

    def test_lt(self):
        self.assertTrue(ref1.__lt__(ref13))
        self.assertFalse(ref1.__lt__(ref14))
        self.assertTrue(ref1.__lt__(ref15))
        self.assertFalse(ref1.__lt__(ref5))

    def test_ispair(self):
        self.assertFalse(ref1.is_pair(ref6))
        self.assertFalse(ref1.is_pair(ref11))
        self.assertFalse(ref1.is_pair(ref5))
        self.assertTrue(ref1.is_pair(ref7))
