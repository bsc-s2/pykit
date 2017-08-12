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
