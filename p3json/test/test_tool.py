import os
import sys
import textwrap
import unittest
from test import test_support
from test.script_helper import assert_python_ok

import subprocess32


class TestTool(unittest.TestCase):
    data = """

        [["blorpie"],[ "whoops" ] , [
                                 ],\t"d-shtaeou",\r"d-nthiouh",
        "i-vhbjkhnth", {"nifty":87}, {"morefield" :\tfalse,"field"
            :"yes"}  ]
           """

    expect = textwrap.dedent("""\
    [
        [
            "blorpie"
        ],
        [
            "whoops"
        ],
        [],
        "d-shtaeou",
        "d-nthiouh",
        "i-vhbjkhnth",
        {
            "nifty": 87
        },
        {
            "field": "yes",
            "morefield": false
        }
    ]
    """)

    expect2 = textwrap.dedent("""\
    [
        [
            "blorpie"
        ],
        [
            "whoops"
        ],
        [],
        "d-shtaeou",
        "d-nthiouh",
        "i-vhbjkhnth",
        {
            "nifty": 87
        },
        {
            "morefield": false,
            "field": "yes"
        }
    ]
    """)

    def _assert_expected(self, out, linemode=False):
        # key order in output is uncertained, try either of the possible match.
        expected = [self.expect, self.expect2]
        for exp in expected:
            if linemode:
                if out.splitlines() == exp.encode().splitlines():
                    return
            else:
                if out == exp:
                    return
        else:
            self.fail("out != either of expected. out: \n" + out + "\n expect:\n" + self.expect + "\n" + self.expect2)

    def test_stdin_stdout(self):
        proc = subprocess32.Popen(
            (sys.executable, '-m', 'pykit.p3json.tool'),
            stdin=subprocess32.PIPE, stdout=subprocess32.PIPE)
        out, err = proc.communicate(self.data.encode())
        self._assert_expected(out, linemode=True)
        self.assertEqual(err, None)

    def _create_infile(self):
        infile = test_support.TESTFN
        with open(infile, "w") as fp:
            self.addCleanup(os.remove, infile)
            fp.write(self.data)
        return infile

    def test_infile_stdout(self):
        infile = self._create_infile()
        rc, out, err = assert_python_ok('-m', 'pykit.p3json.tool', infile)
        self._assert_expected(out, linemode=True)
        self.assertEqual(err, b'')

        # "-" for stdout
        rc, out, err = assert_python_ok('-m', 'pykit.p3json.tool', infile, '-')
        self._assert_expected(out, linemode=True)
        self.assertEqual(err, b'')

    def test_infile_outfile(self):
        infile = self._create_infile()
        outfile = test_support.TESTFN + '.out'
        rc, out, err = assert_python_ok('-m', 'pykit.p3json.tool', infile, outfile)
        self.addCleanup(os.remove, outfile)
        with open(outfile, "r") as fp:
            self._assert_expected(fp.read())
        self.assertEqual(out, b'')
        self.assertEqual(err, b'')

    def test_identical_infile_outfile(self):

        infile = self._create_infile()
        outfile = infile
        rc, out, err = assert_python_ok('-m', 'pykit.p3json.tool', infile, outfile)
        with open(outfile, "r") as fp:
            self._assert_expected(fp.read())

        self.assertEqual((out, err), (b'', b''))
