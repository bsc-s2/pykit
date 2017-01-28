#!/usr/bin/env python2
# coding: utf-8

import unittest

import dictutil


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

            ('x', 0,
             {}, {},
             0
             ),

            ('x', 55,
             {}, {},
             55
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

                ('a', 1,  {'a': 1},
                 {'a': 2},
                 ),

                ('$a.$foo', 1,  {},
                 {'aa': {'bar': 1}},
                 ),

                ('$a.$foo', 1.1,  {},
                 {'aa': {'bar': 1.1}},
                 ),

                ('$a.$foo', 'suffix',  {'aa': {'bar': 'prefix-'}},
                 {'aa': {'bar': 'prefix-suffix'}},
                 ),

                ('$a.$foo', ('b', ),  {'aa': {}},
                 {'aa': {'bar': ('b',)}},
                 ),

                ('$a.$foo', ('b', ),  {'aa': {'bar': ('a',)}},
                 {'aa': {'bar': ('a', 'b',)}},
                 ),

                ('$a.$foo', ['b', ],  {'aa': {'bar': ['a', ]}},
                 {'aa': {'bar': ['a', 'b', ]}},
                 ),

        )

        _vars = {'foo': 'bar',
                 'a': 'aa',
                 }

        for _key_path, _default, _dic, _expect in cases:

            _set = dictutil.make_setter(_key_path, value=_default, incr=True)
            rst = _set(_dic, vars=_vars)

            self.assertEqual(_expect, _dic,
                             'input: {_key_path}, {_dic}; expected dict: {_expect}, actual: {rst}'.format(
                                 _key_path=repr(_key_path),
                                 _dic=repr(_dic),
                                 _expect=repr(_expect),
                                 rst=repr(rst),
                             )
                             )
