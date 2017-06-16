from pykit.p3json.test import PyTest


# from http://json.org/JSON_checker/test/pass2.json
JSON = r'''
[[[[[[[[[[[[[[[[[[["Not too deep"]]]]]]]]]]]]]]]]]]]
'''

class TestPass2(object):
    def test_parse(self):
        # test in/out equivalence and parsing
        res = self.loads(JSON)
        out = self.dumps(res)
        self.assertEqual(res, self.loads(out))


class TestPyPass2(TestPass2, PyTest): pass
