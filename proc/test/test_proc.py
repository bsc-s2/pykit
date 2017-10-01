import os
import time
import unittest

from pykit import proc
from pykit import ututil

dd = ututil.dd

this_base = os.path.dirname(__file__)


class TestProcError(unittest.TestCase):

    foo_fn = '/tmp/foo'

    def _read_file(self, fn):
        try:
            with open(fn, 'r') as f:
                cont = f.read()
                return cont
        except EnvironmentError:
            return None

    def _clean(self):

        # remove written file
        try:
            os.unlink(self.foo_fn)
        except EnvironmentError:
            pass

    def setUp(self):
        self._clean()

    def tearDown(self):
        self._clean()

    def test_procerror(self):
        ex_args = (1, 'out', 'err', 'ls', ('a', 'b'), {"close_fds": True})
        ex = proc.ProcError(*ex_args)

        self.assertEqual(ex_args, (ex.returncode,
                                   ex.out,
                                   ex.err,
                                   ex.command,
                                   ex.arguments,
                                   ex.options))

        self.assertEqual(ex_args, ex.args)

    def test_code_out_err(self):

        subproc = os.path.join(this_base, 'subproc.py')

        returncode, out, err = proc.command('python2', subproc, '222')

        self.assertEqual(222, returncode)
        self.assertEqual('out-1\nout-2\n', out)
        self.assertEqual('err-1\nerr-2\n', err)

        try:
            returncode, out, err = proc.command_ex('python2', subproc, '222')
        except proc.ProcError as e:
            self.assertEqual(222, e.returncode)
            self.assertEqual('out-1\nout-2\n', e.out)
            self.assertEqual('err-1\nerr-2\n', e.err)
            self.assertEqual('python2', e.command)
            self.assertTrue(e.arguments[0].endswith('subproc.py'))
            self.assertEqual('222', e.arguments[1])
            self.assertEqual({}, e.options)
        else:
            self.fail('expect proc.ProcError to be raised')

        returncode, out, err = proc.command_ex('python2', subproc, '0')
        self.assertEqual(0, returncode)
        self.assertEqual('out-1\nout-2\n', out)
        self.assertEqual('err-1\nerr-2\n', err)

        returncode, out, err = proc.command('python2', subproc, '0')

        self.assertEqual(0, returncode)
        self.assertEqual('out-1\nout-2\n', out)
        self.assertEqual('err-1\nerr-2\n', err)

    def test_close_fds(self):

        read_fd = os.path.join(this_base, 'read_fd.py')

        with open(read_fd) as f:
            fd = f.fileno()

            returncode, out, err = proc.command(
                'python2', read_fd, str(fd), close_fds=False)

            self.assertEqual(0, returncode)
            self.assertEqual('###\n', out)
            self.assertEqual('', err)

            returncode, out, err = proc.command(
                'python2', read_fd, str(fd), close_fds=True)

            self.assertEqual(1, returncode)
            self.assertEqual('errno=9\n', out)
            self.assertEqual('', err)

    def test_cwd(self):

        returncode, out, err = proc.command(
            'python2', 'subproc.py', '111', cwd=this_base)
        self.assertEqual(111, returncode)

        returncode, out, err = proc.command('python2', 'subproc.py', '111')
        # can not find subproc.py
        self.assertEqual(2, returncode)

    def test_env(self):
        returncode, out, err = proc.command('python2', 'print_env.py', 'abc',
                                            env={"abc": "xyz"},
                                            cwd=this_base)
        dd('returncode:', returncode)
        dd('out:', out)
        dd('err:', err)

        self.assertEqual(0, returncode)
        self.assertEqual('xyz\n', out)

    def test_stdin(self):

        returncode, out, err = proc.command('python2', 'read_fd.py', '0',
                                            stdin='abc',
                                            cwd=this_base)
        dd('returncode:', returncode)
        dd('out:', out)
        dd('err:', err)

        self.assertEqual(0, returncode)
        self.assertEqual('abc\n', out)

    def test_shell_script(self):

        returncode, out, err = proc.shell_script(
            'ls ' + this_base + ' | grep init | grep -v pyc')

        dd('returncode:', returncode)
        dd('out:', out)
        dd('err:', err)

        self.assertEqual(0, returncode)
        self.assertEqual('__init__.py\n', out)

    def test_start_process(self):

        cases = (
            ('python2', this_base + '/write.py', ['foo'], 'foo'),
            ('python2', this_base + '/write.py', ['foo', 'bar'], 'foobar'),
            ('sh', this_base + '/write.sh', ['123'], '123'),
            ('sh', this_base + '/write.sh', ['123', '456'], '123456'),
        )

        for cmd, target, args, expected in cases:
            proc.start_process(cmd, target, os.environ, *args)
            time.sleep(0.1)
            self.assertEqual(expected, self._read_file(self.foo_fn))
