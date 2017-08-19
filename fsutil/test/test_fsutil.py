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

    def test_get_all_mountpoint(self):
        mps = fsutil.get_all_mountpoint()
        dd('mount points:', mps)
        self.assertIn('/', mps)

        mpsall = fsutil.get_all_mountpoint(all=True)
        dd('all mount points:', mps)

        self.assertTrue(len(mpsall) > len(mps))
        self.assertEqual(set([]), set(mps) - set(mpsall))

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

    def test_get_device_fs(self):

        rc, out, err = proc.shell_script('mount | grep " on / " | grep -o "[^ ]*"')
        dd('find device on /', rc, out, err)

        dev = out.strip()
        dd('device: ', dev)
        rst = fsutil.get_device_fs(dev)
        self.assertTrue(rst in ('hfs', 'xfs', 'ext2', 'ext3', 'ext4'))

    def test_get_path_fs(self):

        rst = fsutil.get_path_fs('/dev')
        dd('fs of /dev: ', rst)
        self.assertNotEqual('unknown', rst)
        self.assertTrue('dev' in rst)

        rst = fsutil.get_path_fs('/blabla')
        dd('fs of /blabla: ', rst)
        self.assertTrue(rst in ('hfs', 'xfs', 'ext2', 'ext3', 'ext4'))


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

    def test_read_write_file(self):

        fn = '/tmp/pykit-ut-rw-file'

        try:
            os.unlink(fn)
        except:
            pass

        dd('write/read file')
        fsutil.write_file(fn, '123')
        self.assertEqual('123', fsutil.read_file(fn))

        dd('write/read 3MB file')
        cont = '123' * (1024**2)

        fsutil.write_file(fn, cont)
        self.assertEqual(cont, fsutil.read_file(fn))

        dd('write file with uid/gid')
        fsutil.write_file(fn, '1', uid=1, gid=1)
        stat = os.stat(fn)
        self.assertEqual(1, stat.st_uid)
        self.assertEqual(1, stat.st_gid)

        try:
            os.unlink(fn)
        except:
            pass
