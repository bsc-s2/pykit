#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit import dictutil
from pykit import ututil

dd = ututil.dd


class TestDictDeepIter(unittest.TestCase):

    def test_depth_iter_default(self):

        cases = (
            ({}, []),
            ({'k1': 'v1'}, [(['k1'], 'v1')]),
            ({'k1': 'v1', 'k2': 'v2'}, [(['k2'], 'v2'), (['k1'], 'v1')]),
            ({'k1': {'k11': 'v11'}, 'k2': 'v2'},
             ([(['k2'], 'v2'), (['k1', 'k11'], 'v11')]),
             )
        )

        for _in, _out in cases:

            idx = 0

            for rst in dictutil.depth_iter(_in):
                self.assertEqual(
                    _out[idx],
                    rst,
                    ('input: {_in}, output: {rst}, expected: {_out}').format(
                        _in=repr(_in),
                        _out=repr(rst),
                        rst=repr(_out[idx])
                    )
                )

                idx = idx + 1

    def test_depth_iter_ks(self):

        idx = 0
        ks = ['mykey']

        _in = {'k1': {'k11': 'v11'}, 'k2': 'v2'}
        _out = [(['mykey', 'k2'], 'v2'), (['mykey', 'k1', 'k11'], 'v11')]
        _mes = 'test argument ks in dictutil.dict_depth_iter()'

        for rst in dictutil.depth_iter(_in, ks=ks):
            self.assertEqual(
                _out[idx],
                rst,
                ('input: {_in}, output: {rst}, expected: {_out},'
                 'message: {_mes}').format(
                     _in=repr(_in),
                     _out=repr(rst),
                     rst=repr(_out[idx]),
                     _mes=_mes
                )
            )

            idx = idx + 1

    def test_depth_iter_maxdepth(self):

        idx = 0

        _in = {'k1': {'k11': {'k111': {'k1111': 'v1111'}}}}
        _out = [(['k1'], {'k11': {'k111': {'k1111': 'v1111'}}}),
                (['k1', 'k11'], {'k111': {'k1111': 'v1111'}}),
                (['k1', 'k11', 'k111'], {'k1111': 'v1111'}),
                (['k1', 'k11', 'k111', 'k1111'], 'v1111')
                ]

        for depth in range(1, 5):
            for rst in dictutil.depth_iter(_in, maxdepth=depth):
                self.assertEqual(
                    _out[idx],
                    rst,
                    'input:: {_in}, output: {rst}, expected: {_out}'.format(
                        _in=repr(_in),
                        rst=repr(rst),
                        _out=repr(_out[idx])
                    )
                )

            idx = idx + 1

    def test_depth_iter_intermediate(self):

        idx = 0

        _in = {'k1': {'k11': {'k111': {'k1111': 'v1111'}}}}
        _out = [(['k1'], {'k11': {'k111': {'k1111': 'v1111'}}}),
                (['k1', 'k11'], {'k111': {'k1111': 'v1111'}}),
                (['k1', 'k11', 'k111'], {'k1111': 'v1111'}),
                (['k1', 'k11', 'k111', 'k1111'], 'v1111')
                ]

        for rst in dictutil.depth_iter(_in, intermediate=True):
            self.assertEqual(
                _out[idx],
                rst)

            idx = idx + 1


class TestDictBreadthIter(unittest.TestCase):

    def test_breadth_iter_default(self):

        cases = (
            ({}, []),
            ({'k1': 'v1'}, [(['k1'], 'v1')]),
            ({'k1': 'v1', 'k2': 'v2'}, [(['k2'], 'v2'), (['k1'], 'v1')]),
            ({'k1': {'k11': 'v11'}, 'k2': 'v2'},
             ([(['k2'], 'v2'),
               (['k1'], {'k11': 'v11'}),
               (['k1', 'k11'], 'v11')
               ])
             )
        )

        for _in, _out in cases:

            idx = 0

            for rst in dictutil.breadth_iter(_in):
                self.assertEqual(
                    _out[idx],
                    rst,
                    ('input: {_in}, output: {rst}, expected: {_out}').format(
                        _in=repr(_in),
                        _out=repr(rst),
                        rst=repr(_out[idx]),
                    )
                )

                idx = idx + 1


class TestGetter(unittest.TestCase):

    def test_getter_str(self):

        cases = (
            ('',
             'lambda dic, vars={}: dic'
             ),

            ('.',
             'lambda dic, vars={}: dic.get("", {}).get("", vars.get("_default", 0))'
             ),

            ('x',
             'lambda dic, vars={}: dic.get("x", vars.get("_default", 0))'
             ),

            ('x.y',
             'lambda dic, vars={}: dic.get("x", {}).get("y", vars.get("_default", 0))'
             ),

            ('x.y.zz',
             'lambda dic, vars={}: dic.get("x", {}).get("y", {}).get("zz", vars.get("_default", 0))'
             ),

            # dynamic
            ('$',
             'lambda dic, vars={}: dic.get(str(vars.get("", "_")), vars.get("_default", 0))'
             ),

            ('$xx',
             'lambda dic, vars={}: dic.get(str(vars.get("xx", "_")), vars.get("_default", 0))'
             ),

            ('$xx.$yy',
             'lambda dic, vars={}: dic.get(str(vars.get("xx", "_")), {}).get(str(vars.get("yy", "_")), vars.get("_default", 0))'
             ),
        )

        for _in, _out in cases:

            rst = dictutil.make_getter_str(_in)

            self.assertEqual(_out, rst,
                             'input: {_in}, expected: {_out}, actual: {rst}'.format(
                                 _in=repr(_in),
                                 _out=repr(_out),
                                 rst=repr(rst),
                             )
                             )

    def test_getter_str_default(self):

        cases = (

            ('x', None,
             'lambda dic, vars={}: dic.get("x", vars.get("_default", None))'
             ),

            ('x', 1,
             'lambda dic, vars={}: dic.get("x", vars.get("_default", 1))'
             ),

            ('x', True,
             'lambda dic, vars={}: dic.get("x", vars.get("_default", True))'
             ),

            ('x', "abc",
             'lambda dic, vars={}: dic.get("x", vars.get("_default", \'abc\'))'
             ),

        )

        for _in, _default, _out in cases:

            rst = dictutil.make_getter_str(_in, default=_default)

            self.assertEqual(_out, rst,
                             'input: {_in}, {_default}, expected: {_out}, actual: {rst}'.format(
                                 _in=repr(_in),
                                 _default=repr(_default),
                                 _out=repr(_out),
                                 rst=repr(rst),
                             )
                             )

    def test_getter_vars(self):

        cases = (

            ('', 0,
             {"x": 1}, {},
             {"x": 1}
             ),

            ('x', 0,
             {}, {},
             0
             ),

            ('x', 0,
             {'x': {'y': 3}}, {},
             {'y': 3}
             ),

            ('x', 55,
             {}, {},
             55
             ),

            ('x', 55,
             {}, {'_default': 66},
             66
             ),

            ('x', 55,
             {"x": 1}, {},
             1
             ),

            ('x.y', 55,
             {"x": {"y": 3}}, {},
             3
             ),

            ('x.z', 55,
             {"x": {"y": 3}}, {},
             55
             ),

            ('x.$v', 55,
             {"x": {"y": 3}}, {},
             55
             ),

            ('x.$var_name', 55,
             {"x": {"y": 3}}, {"var_name": "y"},
             3
             ),

            ('x.$var_name.z', 55,
             {"x": {"y": {}}}, {"var_name": "y"},
             55
             ),

            ('x.$var_name.z', 55,
             {"x": {"y": {"z": 4}}}, {"var_name": "y"},
             4
             ),

        )

        for _in, _default, _dic, _vars, _out in cases:

            acc = dictutil.make_getter(_in, default=_default)

            rst = acc(_dic, vars=_vars)

            self.assertEqual(_out, rst,
                             'input: {_in}, {_default}, {_dic}, {_vars} expected: {_out}, actual: {rst}'.format(
                                 _in=repr(_in),
                                 _default=repr(_default),
                                 _dic=repr(_dic),
                                 _vars=repr(_vars),
                                 _out=repr(_out),
                                 rst=repr(rst),
                             )
                             )

            # test dictutil.get() with the same set of cases

            rst = dictutil.get(_dic, _in, vars=_vars, default=_default)
            dd('dictutil.get({dic}, {key_path} vars={vars}, default={default})'.format(
                dic=_dic,
                key_path=_in,
                vars=_vars,
                default=_default,
            ))
            dd(rst)

            self.assertEqual(_out, rst,
                             'input: {_in}, {_default}, {_dic}, {_vars} expected: {_out}, actual: {rst}'.format(
                                 _in=repr(_in),
                                 _default=repr(_default),
                                 _dic=repr(_dic),
                                 _vars=repr(_vars),
                                 _out=repr(_out),
                                 rst=repr(rst),
                             )
                             )

    def test_get_ignore_vars_key_error(self):

        cases = (
                ({}, '$a', {"a": "x"}, None, 0),
                ({}, '$a', {"a": "x"}, True, 0),
        )

        for case in cases:

            dd('case: ', case)

            dic, key_path, vars, ign, expected = case
            rst = dictutil.get(dic, key_path, vars=vars, ignore_vars_key_error=ign)

            dd('rst: ', rst)

            self.assertEqual(expected, rst)

        with self.assertRaises(KeyError):
            dictutil.get({}, '$a', {}, ignore_vars_key_error=False)


class TestSetter(unittest.TestCase):

    def test_empty_key_path(self):
        try:
            dictutil.make_setter('')
        except KeyError:
            pass
        else:
            self.fail('expect ValueError')

    def test_setter(self):

        cases = (

                ('a', {},
                 3,
                 {'a': 3},
                 ),

                ('a', {'exist': 44},
                 3,
                 {'a': 3, 'exist': 44},
                 ),

                ('a.b.c', {'exist': 44},
                 3,
                 {'a': {'b': {'c': 3}}, 'exist': 44},
                 ),

                ('a.b.c', {'a': {'exist': 44}},
                 3,
                 {'a': {'b': {'c': 3}, 'exist': 44}},
                 ),

        )

        for _key_path, _dic, _value, _expect in cases:

            _set = dictutil.make_setter(_key_path)
            rst = _set(_dic, _value)

            self.assertEqual(_value, rst,
                             'input: {_key_path}, {_dic}; expected return value: {_value}, actual: {rst}'.format(
                                 _key_path=repr(_key_path),
                                 _dic=repr(_dic),
                                 _value=repr(_value),
                                 rst=repr(rst),
                             )
                             )

            self.assertEqual(_expect, _dic,
                             'input: {_key_path}, {_dic}; expected dict: {_expect}, actual: {rst}'.format(
                                 _key_path=repr(_key_path),
                                 _dic=repr(_dic),
                                 _expect=repr(_expect),
                                 rst=repr(rst),
                             )
                             )

    def test_setter_default(self):

        cases = (

                ('a', 'value', {},
                 {'a': 'value'},
                 ),

                ('exist', 'value', {'exist': 44},
                 {'exist': 'value'},
                 ),

                ('a.exist', 'value', {'a': {'exist': 44}},
                 {'a': {'exist': 'value'}},
                 ),

                ('a.exist', lambda *x: '_def', {'a': {'exist': 44}},
                 {'a': {'exist': '_def'}},
                 ),

                ('a.exist', lambda vars: vars.get('foo'), {'a': {'exist': 44}},
                 {'a': {'exist': 'foo'}},
                 ),
        )

        _vars = {'foo': 'foo'}

        for _key_path, _default, _dic, _expect in cases:

            _set = dictutil.make_setter(_key_path, value=_default)
            rst = _set(_dic, vars=_vars)

            if callable(_default):
                _def = _default(_vars)
            else:
                _def = _default

            self.assertEqual(_def, rst,
                             'input: {_key_path}, {_dic}; expected return value: {_def}, actual: {rst}'.format(
                                 _key_path=repr(_key_path),
                                 _dic=repr(_dic),
                                 _def=repr(_def),
                                 rst=repr(rst),
                             )
                             )

            self.assertEqual(_expect, _dic,
                             'input: {_key_path}, {_dic}; expected dict: {_expect}, actual: {rst}'.format(
                                 _key_path=repr(_key_path),
                                 _dic=repr(_dic),
                                 _expect=repr(_expect),
                                 rst=repr(rst),
                             )
                             )

            rst = _set(_dic, 'specified', vars=_vars)
            self.assertEqual('specified', rst)

    def test_setter_vars_inexistent(self):

        _set = dictutil.make_setter('$a')

        try:
            _set({}, vars={})
        except KeyError:
            pass
        else:
            self.fail('inexistent key should raise key error')

    def test_setter_vars(self):

        cases = (

                ('$a', 1,  {},
                 {'aa': 1},
                 ),

                ('$a.$foo', 1,  {},
                 {'aa': {'bar': 1}},
                 ),

        )

        _vars = {'foo': 'bar',
                 'a': 'aa',
                 }

        for _key_path, _default, _dic, _expect in cases:

            _set = dictutil.make_setter(_key_path, value=_default)
            rst = _set(_dic, vars=_vars)

            if callable(_default):
                _def = _default(_vars)
            else:
                _def = _default

            self.assertEqual(_def, rst,
                             'input: {_key_path}, {_dic}; expected return value: {_def}, actual: {rst}'.format(
                                 _key_path=repr(_key_path),
                                 _dic=repr(_dic),
                                 _def=repr(_def),
                                 rst=repr(rst),
                             )
                             )

            self.assertEqual(_expect, _dic,
                             'input: {_key_path}, {_dic}; expected dict: {_expect}, actual: {rst}'.format(
                                 _key_path=repr(_key_path),
                                 _dic=repr(_dic),
                                 _expect=repr(_expect),
                                 rst=repr(rst),
                             )
                             )

            rst = _set(_dic, 'specified', vars=_vars)
            self.assertEqual('specified', rst)

    def test_setter_incr(self):

        cases = (

                ('a', 1, {},
                 {'a': 1},
                 ),

                ('a', 1, {'a': 1},
                 {'a': 2},
                 ),

                ('a', 'foo', {},
                 {'a': 'foo'},
                 ),

                ('a', 'foo', {'a': 'bar'},
                 {'a': 'barfoo'},
                 ),

                ('a', (1, 2), {},
                 {'a': (1, 2)},
                 ),

                ('a', (1, 2), {'a': (0, 1)},
                 {'a': (0, 1, 1, 2)},
                 ),

                ('a', [1, 2], {},
                 {'a': [1, 2]},
                 ),

                ('a', [1, 2], {'a': [0, 1]},
                 {'a': [0, 1, 1, 2]},
                 ),

                ('$a.$foo', 1, {},
                 {'aa': {'bar': 1}},
                 ),

                ('$a.$foo', 1.1, {},
                 {'aa': {'bar': 1.1}},
                 ),

                ('$a.$foo', 'suffix', {'aa': {'bar': 'prefix-'}},
                 {'aa': {'bar': 'prefix-suffix'}},
                 ),

                ('$a.$foo', ('b',), {'aa': {}},
                 {'aa': {'bar': ('b',)}},
                 ),

                ('$a.$foo', ('b',), {'aa': {'bar': ('a',)}},
                 {'aa': {'bar': ('a', 'b',)}},
                 ),

                ('$a.$foo', ['b', ], {'aa': {'bar': ['a', ]}},
                 {'aa': {'bar': ['a', 'b', ]}},
                 ),

        )

        _vars = {'foo': 'bar',
                 'a': 'aa',
                 }

        for _key_path, _default, _dic, _expect in cases:

            dd(_key_path, _default, _dic, _expect)

            _set = dictutil.make_setter(_key_path, value=_default, incr=True)
            rst = _set(_dic, vars=_vars)
            dd('rst:', rst)

            self.assertEqual(_expect, _dic,
                             'input: {_key_path}, {_dic}; expected dict: {_expect}, actual: {rst}'.format(
                                 _key_path=repr(_key_path),
                                 _dic=repr(_dic),
                                 _expect=repr(_expect),
                                 rst=repr(rst),
                             )
                             )


class TestAttrDict(unittest.TestCase):

    def test_attrdict(self):

        cases = (
                ([],
                 {},
                 {}
                 ),

                ([],
                 {'a': 2},
                 {'a': 2}
                 ),

                ([{'x': 2}],
                 {'a': 4},
                 {'x': 2, 'a': 4},
                 ),
        )

        for args, kwargs, expected in cases:
            rst = dictutil.attrdict(*args, **kwargs)
            self.assertEqual(expected, rst,
                             'input: {a} {kw} {e}, rst: {rst}'.format(
                                 a=args, kw=kwargs, e=expected, rst=rst))

            for k in rst:
                self.assertEqual(rst[k], getattr(rst, k))

    def test_dict_method(self):

        ad = dictutil.attrdict(a=1, b=2)

        self.assertEqual(['a', 'b'], ad.keys())
        self.assertEqual([1, 2], ad.values())
        self.assertEqual([('a', 1), ('b', 2)], ad.items())

    def test_recursive(self):

        ad = dictutil.attrdict(
            x=1, y={'a': 3, 'b': dict(c=4), 'd': dictutil.attrdict(z=5)})

        self.assertEqual(1, ad.x)
        self.assertEqual({'a': 3, 'b': {'c': 4}, 'd': {'z': 5}}, ad.y)
        self.assertEqual(3, ad.y.a)
        self.assertEqual(4, ad.y.b.c)
        self.assertEqual(5, ad.y.d.z)

    def test_writable(self):

        ad = dictutil.attrdict(a={}, b={1: 2})
        ad['x'] = 4
        self.assertEqual(4, ad.x)
        self.assertEqual(4, ad['x'])
        ad.y = 5
        self.assertEqual(5, ad.y)
        self.assertEqual(5, ad['y'])

    def test_attrdict_copy(self):

        # reference type value are always copied when accessing

        ad = dictutil.attrdict_copy(a={}, b={'x': {'foo': 'bar'}})
        self.assertIsNot(ad.a, ad.a)
        self.assertIsNot(ad.b.x, ad.b.x)
        self.assertIsNot(ad['a'], ad['a'])
        self.assertIsNot(ad['b']['x'], ad['b']['x'])

        # value got is still a AttrDictCopy instance

        b = ad.b
        self.assertIsNot(b.x, b.x)
        self.assertIsNot(b['x'], b['x'])

        # it does not change the original value

        with self.assertRaises(KeyError):
            ad['b'] = 10

        with self.assertRaises(KeyError):
            ad.b['x'] = 10

        with self.assertRaises(KeyError):
            b['x'] = 10

        with self.assertRaises(AttributeError):
            ad.b = 10

        with self.assertRaises(AttributeError):
            ad.b.x = 10

        with self.assertRaises(AttributeError):
            ad.y = 2

    def test_attrdict_copy_as_dict(self):

        ad = dictutil.attrdict_copy(a={}, b={'x': {}})
        d = ad.as_dict()

        b2 = d['b']
        d['b']['x'] = 100
        self.assertEqual(100, b2['x'])

    def test_attr_overriding(self):

        ad = dictutil.attrdict(items=1)

        with self.assertRaises(TypeError):
            ad.items()

    def test_ref_to_same_item(self):

        x = {'a': 1}
        ad = dictutil.attrdict(u=x, v=x)

        self.assertIs(ad.u, ad.v)

        x['x'] = x
        ad = dictutil.attrdict(x)

        self.assertTrue(isinstance(ad, dictutil.AttrDict))
        self.assertTrue(isinstance(ad.x, dictutil.AttrDict))
        self.assertTrue(ad.x is not ad, 'attrdict does create a new dict')
        self.assertTrue(ad.x.x is ad.x, 'circular references work for all dict items.')
        self.assertTrue(ad.x.x.x is ad.x.x, 'circular references work for all dict items.(2)')


class TestIsSubDict(unittest.TestCase):

    def test_dict(self):

        for case in [
            (1, 1, True),
            (1, 2, False),
            ("x", "x", True),
            ("x", "b", False),
            (None, None, True),

            ({"a": 1}, {"a": 1}, True),
            ({}, {"a": None}, False),
            ({"a": 1}, {}, True),
            ({"a": 1}, None, False),
            (None, {"a": 1}, False),

            ({"a": (1, 2)}, {"a": (1, 2)}, True),
            ({"a": (1, 2, 3)}, {"a": (1, 2)}, True),

            ({"a": 1}, [], False),
            ({"a": [1, (2, 3)]}, {"a": [1, (2,)]}, True),
            ({"a": [1, (2, 3)]}, {"a": [1, (2, 4)]}, False),
            ({"a": [1, (2, 3)]}, {"a": [1, (2, 3, 4)]}, False),

            ({"a": 1, "b": 2}, {"a": 1}, True),
            ({"a": 1}, {"a": 1, "b": 2}, False),
            ({"a": 1, "b": {"c": 3, "d": 4}}, {"a": 1, "b": {"d": 4}}, True),
            ({"a": 1, "b": {"c": 3, "d": 4}}, {"a": 1, "b": 2}, False),
        ]:
            self.assertEqual(dictutil.contains(case[0], case[1]), case[2])

    def test_recursive_dict(self):
        a = {}
        a[1] = {}
        a[1][1] = a

        b = {}
        b[1] = {}
        b[1][1] = {}
        b[1][1][1] = b

        self.assertEqual(dictutil.contains(a, b), True)

    def test_recursive_dict_with_list(self):
        a = {'k': [0, 2]}
        a['k'][0] = {'k': [0, 2]}
        a['k'][0]['k'][0] = a

        b = {'k': [0, 2]}
        b['k'][0] = b

        self.assertEqual(dictutil.contains(a, b), True)
