import os
import unittest

from pykit import fsutil
from pykit import humannum
from pykit import proc
from pykit import ututil

dd = ututil.dd

# xx/pykit/fsutil/test/
this_base = os.path.dirname(__file__)

pyt = 'python2'


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

        rc, out, err = proc.shell_script(
            'mount | grep " on / " | grep -o "[^ ]*"')
        dd('find device on /', rc, out, err)

        dev = out.strip()
        dd('device: ', dev)
        rst = fsutil.get_device_fs(dev)
        self.assertIn(rst, ('hfs', 'xfs', 'ext2', 'ext3', 'ext4'))

    def test_get_path_fs(self):

        rst = fsutil.get_path_fs('/dev')
        dd('fs of /dev: ', rst)
        self.assertNotEqual('unknown', rst)
        self.assertTrue('dev' in rst)

        rst = fsutil.get_path_fs('/blabla')
        dd('fs of /blabla: ', rst)
        self.assertIn(rst, ('hfs', 'xfs', 'ext2', 'ext3', 'ext4'))

    def test_get_path_usage(self):

        path = '/'
        rst = fsutil.get_path_usage(path)
        dd(humannum.humannum(rst))

        # check against os.statvfs.

        st = os.statvfs(path)

        self.assertEqual(st.f_frsize * st.f_bavail, rst['available'])
        self.assertEqual(st.f_frsize * st.f_blocks, rst['total'])
        self.assertEqual(st.f_frsize * (st.f_blocks - st.f_bavail), rst['used'])
        self.assertEqual((st.f_blocks - st.f_bavail) * 100 / st.f_blocks, int(rst['percent'] * 100))

        if st.f_bfree > st.f_bavail:
            self.assertLess(rst['available'], st.f_frsize * st.f_bfree)
        else:
            dd('st.f_bfree == st.f_bavail')

        # check against df

        rc, out, err = proc.shell_script('df -m / | tail -n1')
        # Filesystem 1M-blocks   Used Available Capacity  iused    ifree %iused  Mounted on
        # /dev/disk1    475828 328021    147556    69% 84037441 37774557   69%   /
        dd('space of "/" from df')
        total_mb = out.strip().split()[1]

        # "123.8M", keep int only
        rst_total_mb = humannum.humannum(rst['total'], unit=humannum.M)
        rst_total_mb = rst_total_mb.split('.')[0].split('M')[0]

        dd('total MB from df:', total_mb, 'result total MB:', rst_total_mb)

        self.assertEqual(total_mb, rst_total_mb)

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

    def test_makedirs_with_config(self):

        fn = '/tmp/pykit-ut-fsutil-foo'
        force_remove(fn)

        rc, out, err = proc.shell_script(pyt + ' ' + this_base + '/makedirs_with_config.py ' + fn,
                                         env=dict(PYTHONPATH=this_base + ':' + os.environ.get('PYTHONPATH'))
                                         )

        dd('run makedirs_with_config.py: ', rc, out, err)

        self.assertEqual(0, rc, 'normal exit')
        self.assertEqual('2,3', out, 'uid,gid is defined in test/pykitconfig.py')

    def test_read_write_file(self):

        fn = '/tmp/pykit-ut-rw-file'
        force_remove(fn)

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

        force_remove(fn)

    def test_write_file_with_config(self):

        fn = '/tmp/pykit-ut-fsutil-foo'
        force_remove(fn)

        rc, out, err = proc.shell_script(pyt + ' ' + this_base + '/write_with_config.py ' + fn,
                                         env=dict(PYTHONPATH=this_base + ':' + os.environ.get('PYTHONPATH'))
                                         )

        dd('run write_with_config.py: ', rc, out, err)

        self.assertEqual(0, rc, 'normal exit')
        self.assertEqual('2,3', out, 'uid,gid is defined in test/pykitconfig.py')

        force_remove(fn)


def force_remove(fn):

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
