from pykit.p3json.test import PyTest


class TestDefault(object):
    def test_default(self):
        self.assertEqual(
            self.dumps(type, default=repr),
            self.dumps(repr(type)))


class TestPyDefault(TestDefault, PyTest): pass
