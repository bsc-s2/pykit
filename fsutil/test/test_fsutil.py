#!/usr/bin/env python2
# coding: utf-8

import os
import time
import unittest

from pykit import fsutil
from pykit import humannum
from pykit import proc
from pykit import threadutil
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

        notall = fsutil.get_disk_partitions(all=False)
        self.assertTrue(len(rst) > len(notall))
        self.assertEqual(set([]), set(notall) - set(rst))

    def test_get_device(self):

        rst = fsutil.get_device('/inexistent')

        # GNU "grep -o" split items into several lines
        root_dev = proc.shell_script(
            'mount | grep " on / " | grep -o "[^ ]*" | head -n1')[1].strip()

        self.assertEqual(root_dev, rst)

    def test_get_device_fs(self):

        # GNU "grep -o" split items into several lines
        rc, out, err = proc.shell_script(
            'mount | grep " on / " | grep -o "[^ ]*" | head -n1')
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

        # check against os.statvfs.
        st = os.statvfs(path)

        dd(humannum.humannum(rst))

        # space is changing..

        self.assertAlmostEqual(st.f_frsize * st.f_bavail, rst['available'], delta=4 * 1024**2)
        self.assertAlmostEqual(st.f_frsize * st.f_blocks, rst['total'], delta=4 * 1024**2)
        self.assertAlmostEqual(st.f_frsize * (st.f_blocks - st.f_bavail), rst['used'], delta=4 * 1024**2)
        self.assertAlmostEqual((st.f_blocks - st.f_bavail) * 100 / st.f_blocks,
                               int(rst['percent'] * 100), delta=4 * 1024**2)

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

        self.assertAlmostEqual(int(total_mb), int(rst_total_mb), delta=4)

    def test_get_path_inode_usage(self):

        inode_st = fsutil.get_path_inode_usage('/')

        self.assertGreaterEqual(inode_st['percent'], 0.0, '')
        self.assertLessEqual(inode_st['percent'], 1.0, '')
        self.assertLessEqual(inode_st['used'], inode_st['total'])

        total = inode_st['used'] + inode_st['available']
        self.assertEqual(inode_st['total'], total)

    def test_makedirs(self):

        fn = '/tmp/pykit-ut-fsutil-foo'
        fn_part = ('/tmp', 'pykit-ut-fsutil-foo')
        dd('fn_part:', fn_part)

        force_remove(fn)

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

    def test_get_sub_dirs(self):
        fsutil.makedirs('test_dir/sub_dir1')
        fsutil.makedirs('test_dir/sub_dir2')
        fsutil.write_file('test_dir/test_file', 'foo')

        sub_dirs = fsutil.get_sub_dirs('test_dir')
        self.assertListEqual(['sub_dir1', 'sub_dir2'], sub_dirs)

        fsutil.remove('test_dir')

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

    def test_write_file_atomically(self):

        fn = '/tmp/pykit-ut-fsutil-write-atomic'

        dd('atomically write file')

        cont_thread1 = 'cont_thread1'
        cont_thread2 = 'cont_thread2'

        os_fsync = os.fsync

        def _wait_fsync(fildes):
            time.sleep(3)

            os_fsync(fildes)

        os.fsync = _wait_fsync

        assert_ok = {'ok': True}

        def _write_wait(cont_write, cont_read, start_after, atomic):

            time.sleep(start_after)

            fsutil.write_file(fn, cont_write, atomic=atomic)

            if cont_read != fsutil.read_file(fn):
                assert_ok['ok'] = False

        force_remove(fn)
        # atomic=False
        #  time     file    thread1     thread2
        #   0      cont_1   w_cont_1    sleep()
        #  1.5     cont_2   sleep()     w_cont_2
        #   3      cont_2   return      sleep()
        #  4.5     cont_2    None       return

        ths = []
        th = threadutil.start_daemon_thread(_write_wait,
                                            args=(cont_thread1, cont_thread2, 0, False))
        ths.append(th)

        th = threadutil.start_daemon_thread(_write_wait,
                                            args=(cont_thread2, cont_thread2, 1.5, False))
        ths.append(th)

        for th in ths:
            th.join()
        self.assertTrue(assert_ok['ok'])

        force_remove(fn)
        # atomic=True
        #  time     file    thread1     thread2
        #   0       None    w_cont_1    sleep()
        #  1.5      None    sleep()     w_cont_2
        #   3      cont_1   return      sleep()
        #  4.5     cont_2    None       return

        ths = []
        th = threadutil.start_daemon_thread(_write_wait,
                                            args=(cont_thread1, cont_thread1, 0, True))
        ths.append(th)

        th = threadutil.start_daemon_thread(_write_wait,
                                            args=(cont_thread2, cont_thread2, 1.5, True))
        ths.append(th)

        for th in ths:
            th.join()
        self.assertTrue(assert_ok['ok'])

        os.fsync = os_fsync
        force_remove(fn)

    def test_remove_normal_file(self):

        fn = '/tmp/pykit-ut-fsutil-remove-file-normal'
        force_remove(fn)

        fsutil.write_file(fn, '', atomic=True)
        self.assertTrue(os.path.isfile(fn))

        fsutil.remove(fn)
        self.assertFalse(os.path.exists(fn))

    def test_remove_link_file(self):

        src_fn = '/tmp/pykit-ut-fsutil-remove-file-normal'
        force_remove(src_fn)

        fsutil.write_file(src_fn, '', atomic=True)
        self.assertTrue(os.path.isfile(src_fn))

        link_fn = '/tmp/pykit-ut-fsutil-remove-file-link'
        force_remove(link_fn)

        os.link(src_fn, link_fn)
        self.assertTrue(os.path.isfile(link_fn))

        fsutil.remove(link_fn)
        self.assertFalse(os.path.exists(link_fn))

        symlink_fn = '/tmp/pykit-ut-fsutil-remove-file-symlink'
        force_remove(symlink_fn)

        os.symlink(src_fn, symlink_fn)
        self.assertTrue(os.path.islink(symlink_fn))

        fsutil.remove(symlink_fn)
        self.assertFalse(os.path.exists(symlink_fn))

        force_remove(src_fn)

    def test_remove_dir(self):

        dirname = '/tmp/pykit-ut-fsutil-remove-dir'

        fsutil.makedirs(dirname)
        self.assertTrue(os.path.isdir(dirname))

        for is_dir, file_path in (
                (False, ('normal_file',)),
                (True,  ('sub_dir',)),
                (False, ('sub_dir', 'sub_file1')),
                (False, ('sub_dir', 'sub_file2')),
                (True,  ('sub_empty_dir',)),
                (True,  ('sub_dir', 'sub_sub_dir')),
                (False, ('sub_dir', 'sub_sub_dir', 'sub_sub_file')),
        ):

            path = os.path.join(dirname, *file_path)

            if is_dir:
                fsutil.makedirs(path)
                self.assertTrue(os.path.isdir(path))
            else:
                fsutil.write_file(path, '')
                self.assertTrue(os.path.isfile(path))

        fsutil.remove(dirname)
        self.assertFalse(os.path.exists(dirname))

    def test_remove_dir_with_link(self):

        dirname = '/tmp/pykit-ut-fsutil-remove-dir'

        fsutil.makedirs(dirname)
        self.assertTrue(os.path.isdir(dirname))

        normal_file = 'normal_file'
        normal_path = os.path.join(dirname, normal_file)

        fsutil.write_file(normal_path, '')
        self.assertTrue(os.path.isfile(normal_path))

        hard_link = 'hard_link'
        hard_path = os.path.join(dirname, hard_link)

        os.link(normal_path, hard_path)
        self.assertTrue(os.path.isfile(hard_path))

        symbolic_link = 'symbolic_link'
        symbolic_path = os.path.join(dirname, symbolic_link)

        os.symlink(hard_path, symbolic_path)
        self.assertTrue(os.path.islink(symbolic_path))

        fsutil.remove(dirname)
        self.assertFalse(os.path.exists(dirname))

    def test_remove_error(self):

        dirname = '/tmp/pykit-ut-fsutil-remove-on-error'
        if os.path.isdir(dirname):
            fsutil.remove(dirname)

        # OSError
        self.assertRaises(os.error, fsutil.remove, dirname, False)

        # ignore errors
        fsutil.remove(dirname, ignore_errors=True)

        def assert_error(exp_func):
            def onerror(func, path, exc_info):
                self.assertEqual(func, exp_func)
            return onerror

        # on error
        fsutil.remove(dirname, onerror=assert_error(os.remove))

    def test_calc_checksums(self):

        M = 1024**2

        fn = '/tmp/pykit-ut-fsutil-calc_checksums'
        force_remove(fn)

        cases = (
            ('',
                {
                    'sha1':       True,
                    'md5':        True,
                    'crc32':      True,
                    'sha256':     True,
                    'block_size': M,
                    'io_limit':   M,
                },
                {
                    'sha1':       'da39a3ee5e6b4b0d3255bfef95601890afd80709',
                    'md5':        'd41d8cd98f00b204e9800998ecf8427e',
                    'crc32':      '00000000',
                    'sha256':     'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                },
                None,
             ),

            ('',
                {
                    'md5':        True,
                    'crc32':      True,
                },
                {
                    'sha1':       None,
                    'md5':        'd41d8cd98f00b204e9800998ecf8427e',
                    'crc32':      '00000000',
                    'sha256':     None,
                },
                None,
             ),

            ('',
                {
                },
                {
                    'sha1':       None,
                    'md5':        None,
                    'crc32':      None,
                    'sha256':     None,
                },
                None,
             ),

            ('It  바로 とても 氣!',
                {
                    'sha1':       True,
                    'md5':        True,
                    'crc32':      True,
                    'sha256':     True,
                    'block_size': M,
                    'io_limit':   M,
                },
                {
                    'sha1':       'e22fa5446cb33d0c32221d89ee270dff23e32847',
                    'md5':        '9d245fca88360be492c715253d68ba6f',
                    'crc32':      '7c3becdb',
                    'sha256':     '7327753b12db5c0dd090ad802c1c8ff44ea4cb447f3091d43cab371bd7583d9a',
                },
                None,
             ),

            ('It  바로 とても 氣!',
                {
                    'sha1':       False,
                    'md5':        True,
                    'crc32':      True,
                    'sha256':     False,
                    'block_size': M,
                    'io_limit':   M,
                },
                {
                    'sha1':       None,
                    'md5':        '9d245fca88360be492c715253d68ba6f',
                    'crc32':      '7c3becdb',
                    'sha256':     None,
                },
                None,
             ),

            ('It  바로 とても 氣!',
                {
                    'sha1':       True,
                    'md5':        False,
                    'crc32':      False,
                    'sha256':     True,
                },
                {
                    'sha1':       'e22fa5446cb33d0c32221d89ee270dff23e32847',
                    'md5':        None,
                    'crc32':      None,
                    'sha256':     '7327753b12db5c0dd090ad802c1c8ff44ea4cb447f3091d43cab371bd7583d9a',
                },
                None,
             ),

            ('!' * M * 10,
                {
                    'sha1':       False,
                    'md5':        False,
                    'crc32':      False,
                    'sha256':     False,
                    'block_size': M,
                    'io_limit':   M,
                },
                {
                    'sha1':       None,
                    'md5':        None,
                    'crc32':      None,
                    'sha256':     None,
                },
                (0, 0.5),
             ),

            ('!' * M * 10,
                {
                    'sha1':       True,
                    'md5':        True,
                    'crc32':      True,
                    'sha256':     True,
                    'block_size': M * 10,
                    'io_limit':   M * 10,
                },
                {
                    'sha1':       'c5430d624c498024d0f3371670227a201e910054',
                    'md5':        '8f499b17375fc678c7256f3c0054db79',
                    'crc32':      'f0af209f',
                    'sha256':     'bd5263cc56b27fda9f86f41f6d2ec012eb60d757281003c363b88677c7dcc5e7',

                },
                (1, 1.5),
             ),

            ('!' * M * 10,
                {
                    'sha1':       True,
                    'block_size': M,
                    'io_limit':   M * 5,
                },
                None,
                (2, 2.5),
             ),

            ('!' * M * 10,
                {
                    'sha1':       True,
                    'block_size': M,
                    'io_limit': -1,
                },
                None,
                (0, 0.5),
             ),
        )

        for cont, args, exp_checksums, min_time in cases:

            force_remove(fn)
            fsutil.write_file(fn, cont)

            t0 = time.time()
            checksums = fsutil.calc_checksums(fn, **args)
            spend_time = time.time() - t0

            if exp_checksums is not None:
                for k in checksums:
                    self.assertEqual(exp_checksums[k], checksums[k],
                                     'except: {exp}, actuality: {act}'.format(
                        exp=exp_checksums[k],
                        act=checksums[k],
                    ))

            if min_time is not None:
                self.assertTrue(min_time[0] < spend_time < min_time[1])

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
