import os
import unittest

from pykit import fsutil
from pykit import proc
from pykit import ututil

dd = ututil.dd


class TestFSUtil(unittest.TestCase):

    def test_exceptions(self):

        dd('present: ', fsutil.FSUtilError)
        dd('present: ', fsutil.NotMountPoint)

    def test_mountpoint(self):

        cases = (
                ('/',               '/',),
                ('/bin/ls',         '/',),
                ('/dev',            '/dev',),
                ('/dev/',           '/dev',),
                ('/dev/random',     '/dev',),
                ('/dev/inexistent', '/dev',),
        )

        for path, expected in cases:

            dd(path, ' --> ', expected)

            rst = fsutil.get_mountpoint(path)
            dd('rst: ', rst)

            self.assertEqual(expected, rst)

            # test assert_mount_point

            fsutil.assert_mountpoint(rst)
            self.assertRaises(fsutil.NotMountPoint,
                              fsutil.assert_mountpoint, path + '/aaa')

    def test_get_disk_partitions(self):

        rst = fsutil.get_disk_partitions()

        self.assertIn('/', rst)

        root = rst['/']
        for k in ('device', 'mountpoint', 'fstype', 'opts'):
            self.assertIn(k, root)

    def test_get_device(self):

        rst = fsutil.get_device('/inexistent')

        root_dev = proc.shell_script(
            'mount | grep " on / " | grep -o "[^ ]*"')[1].strip()

        self.assertEqual(root_dev, rst)

    def test_makedirs(self):

        fn = '/tmp/pykit-ut-fsutil-foo'
        fn_part = ('/tmp', 'pykit-ut-fsutil-foo')
        dd('fn_part:', fn_part)

        try:
            os.rmdir(fn)
        except:
            pass

        try:
            os.unlink(fn)
        except:
            pass

        def get_mode(fn):
            mode = os.stat(fn).st_mode
            dd('mode read:', oct(mode))
            return mode & 0777

        dd('file is not a dir')
        with open(fn, 'w') as f:
            f.write('a')
        self.assertRaises(OSError, fsutil.makedirs, fn)
        os.unlink(fn)

        dd('no error if dir exist')
        os.mkdir(fn)
        fsutil.makedirs(fn)
        os.rmdir(fn)

        dd('single part path should be created')
        fsutil.makedirs(fn)
        self.assertTrue(os.path.isdir(fn))
        os.rmdir(fn)

        dd('multi part path should be created')
        fsutil.makedirs(*fn_part)
        self.assertTrue(os.path.isdir(fn), 'multi part path should be created')
        os.rmdir(fn)

        dd('default mode')
        fsutil.makedirs(fn)
        self.assertEqual(0755, get_mode(fn))
        os.rmdir(fn)

        dd('specify mode')
        fsutil.makedirs(fn, mode=0700)
        self.assertEqual(0700, get_mode(fn))
        os.rmdir(fn)

        dd('specify uid/gid, to change uid, you need root privilege')
        fsutil.makedirs(fn, uid=1, gid=1)
