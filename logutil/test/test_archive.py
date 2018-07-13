import os
import unittest

from pykit import fsutil
from pykit import logutil
from pykit import proc
from pykit import ututil

dd = ututil.dd

class TestArchive(unittest.TestCase):

    testArc = '/tmp/testArc'
    testSrc = '/tmp/testSrc'

    src_fns = ['bar', 'foo', 'hello', 'hi']

    arc_dirs = ['2018-07-01', '2018-07-02', '2018-07-03', '2018-07-04', '2018-07-05']

    # in MB
    testArcSize = 1

    @classmethod
    def setUpClass(cls):

        fsutil.makedirs(cls.testArc)

        # mount testArc to limit it's size
        cmd = "mount -t tmpfs -o size={size}M tmpfs '{_dir}'".format(
                _dir=cls.testArc, size=cls.testArcSize)
        proc.command(cmd, shell=True)

    @classmethod
    def tearDownClass(cls):

        cmd = "umount '{_dir}'".format(_dir=cls.testArc)
        proc.command(cmd, shell=True)

        fsutil.remove(cls.testArc)

    def setUp(self):

        fsutil.makedirs(self.testSrc)

        for fn in self.src_fns:
            fsutil.write_file(os.path.join(self.testSrc, fn), fn)

        for d in self.arc_dirs:
            fsutil.makedirs(os.path.join(self.testArc, d))

    def tearDown(self):

        fsutil.remove(self.testSrc)

        for d in fsutil.get_sub_dirs(self.testArc):
            fsutil.remove(os.path.join(self.testArc, d))

    def test_archive_all(self):

        self.create_archiver().archive()

        arc_path = os.path.join(self.testArc, 'current')
        arc_fns = fsutil.list_fns(arc_path)

        self.assertEqual(len(arc_fns), len(self.src_fns))

        for s, a in zip(self.src_fns, arc_fns):
            self.assertTrue(a.startswith(s))

    def test_archive_files(self):

        self.create_archiver().archive(self.src_fns[:2])

        arc_path = os.path.join(self.testArc, 'current')
        arc_fns = fsutil.list_fns(arc_path)

        self.assertEqual(len(arc_fns), len(self.src_fns[:2]))

        for s, a in zip(self.src_fns[:2], arc_fns):
            self.assertTrue(a.startswith(s))

    def test_clean_free_gb(self):

        min_free_percentage = 0.5

        # self.testArcSize is in MB
        testArcSize_in_b = self.testArcSize * 1024**2
        testArcSize_in_gb = self.testArcSize / 1024.0

        kwargs = {
                'free_gb': testArcSize_in_gb * min_free_percentage,
                'free_percentage': None,
                'free_interp': None,
            }

        min_free = int(testArcSize_in_b * 0.5)

        self.judge_clean(min_free, **kwargs)

    def test_clean_free_pecentage(self):

        min_free_percentage = 0.5
        testArcSize_in_b = self.testArcSize * 1024**2

        kwargs = {
                'free_gb': None,
                'free_percentage': min_free_percentage,
                'free_interp': None,
            }

        min_free = int(testArcSize_in_b * 0.5)

        self.judge_clean(min_free, **kwargs)

    def test_clean_free_interp(self):

        testArcSize_in_b = self.testArcSize * 1024**2

        kwargs = {
                'free_gb': None,
                'free_percentage': None,
                'free_interp': [(2, 10, 30, testArcSize_in_b), (1, 5, 15, testArcSize_in_b/2)],
            }

        min_free = int(testArcSize_in_b * 0.5)

        self.judge_clean(min_free, **kwargs)

    def judge_clean(self, min_free, **kwargs):

        self.writeArc(int(min_free)+1)

        path_stat = fsutil.get_path_usage(self.testArc)
        self.assertLess(path_stat['available'], min_free)

        self.create_archiver(**kwargs).clean()

        path_stat = fsutil.get_path_usage(self.testArc)
        self.assertGreaterEqual(path_stat['available'], min_free)

    def create_archiver(self, **kwargs):

        kwargs['days_to_keep'] = 0
        return logutil.Archiver(self.testSrc, self.testArc, **kwargs)

    def writeArc(self, size):

        fn = os.path.join(self.testArc, self.arc_dirs[-1], 'foo')
        content = os.urandom(size)
        fsutil.write_file(fn, content)
