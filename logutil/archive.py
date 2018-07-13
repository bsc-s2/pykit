#!/usr/bin/env python2
# coding: utf-8

import errno
import logging
import shutil
import time
import os

import numpy

from pykit import fsutil
from pykit import humannum
from pykit import net
from pykit import proc
from pykit import timeutil

logger = logging.getLogger(__name__)

class Archiver(object):

    def __init__(self, src_base, arc_base, time_toleration=600,
            free_gb=20, free_percentage=0, free_interp=None,
            days_to_keep=30, at_most_clean=8):

        self.src_base = src_base
        self.arc_base = arc_base

        self.time_toleration = time_toleration

        self.free_gb = free_gb
        self.free_percentage = free_percentage
        self.free_interp = free_interp

        self.days_to_keep = days_to_keep
        self.at_most_clean = at_most_clean

    def archive(self, src_fns=None):

        if src_fns is None:
            src_fns = [os.path.join(self.src_base, fn) for fn in fsutil.list_fns(self.src_base)]
        else:
            src_fns = [os.path.join(self.src_base, fn) for fn in src_fns]

        for fn in src_fns:
            try:
                self._archive(fn)
            finally:
                try:
                    os.unlink(fn)
                except Exception as e:
                    logger.warn(repr(e) + ' while unlink ' + repr(fn))

    def clean(self):

        arcs = fsutil.get_sub_dirs(self.arc_base)

        arcs = [x for x in arcs
                   if not os.path.islink(os.path.join(self.arc_base, x))]

        arcs_to_clean = self.get_to_clean(arcs)

        path_stat = fsutil.get_path_usage(self.arc_base)
        capa = path_stat['total']
        free = path_stat['available']

        min_free = self.get_min_free()

        _hum = humannum.humannum

        for arc in arcs_to_clean:

            # refresh free space
            path_stat = fsutil.get_path_usage(self.arc_base)

            if path_stat['available'] >= min_free:
                break

            logger.info("to clean archived log to free up to {min_free} space: {arc_base} / {arc}".format(
                        min_free=_hum(min_free),
                        arc_base=self.arc_base,
                        arc=arc,
            ))

            clean_path = os.path.join(self.arc_base, arc)

            try:
                shutil.rmtree(clean_path)
            except Exception as e:
                logger.exception(repr(e) + ' while clean ' + clean_path)

        ctx = ('{_dir} free space: {free} / {capa} requires: free >= {min_free}'
               ' interpolation rule: {free_interp}').format(
                _dir=self.arc_base,
                free=_hum(free),
                capa=_hum(capa),
                min_free=_hum(min_free),
                free_interp=self.free_interp,
        )

        if path_stat['available'] >= min_free:
            logger.info("disk free space is ok: " + ctx)
        else:
            logger.warn('all archived log are removed'
                        ' but there is still not enough free space:' + ctx)

    def get_to_clean(self, arcs):

        for arc in arcs:
            arc_path=os.path.join(self.arc_base, arc)
            is_dir=os.path.isdir(arc_path)

            logger.debug("{arc} {arc_path} isdir: {is_dir}".format(
                    arc=arc,
                    arc_path=arc_path,
                    is_dir=is_dir,
                ))

        toclean = []
        # 1 arc is 1 day's archived log
        assert self.days_to_keep >= 0

        if self.days_to_keep == 0:
            toclean = arcs
        elif len(arcs) > self.days_to_keep:
            toclean = arcs[:-self.days_to_keep]
            logger.info("to clean archived log older than {days} days: {toclean}".format(
                    days=self.days_to_keep,
                    toclean=toclean,
            ))

        return toclean[:self.at_most_clean]

    def get_min_free(self):

        path_stat = fsutil.get_path_usage(self.arc_base)

        if self.free_interp is not None:
            min_free = self.calc_interp(path_stat['total'])

        elif self.free_gb is not None:
            min_free = self.free_gb * (1024 ** 3)

        elif self.free_percentage is not None:
            min_free = path_stat['total'] * self.free_percentage

        else:
            assert False, 'one of free_interp, free_gb, free_percentage must be specified'

        return min_free

    def calc_interp(self, capa):

        if self.free_interp is None:
            return None

        xp, yp = self.free_interp
        _parse = humannum.parsenum

        xp = [_parse(x) for x in xp]
        yp = [_parse(y) for y in yp]

        # if yp is in percentage
        yp = [(y if y > 1 else y * xp[i])
            for i, y in enumerate(yp)]

        return numpy.interp(capa, xp, yp)

    def _archive(self, src_path):

        arc_dir = self.make_arc_dir()
        arc_fn = self.make_arc_fn(src_path)
        arc_path = os.path.join(arc_dir, arc_fn)

        cmd = "gzip -c '{src}' >> '{dst}'".format(src=src_path, dst=arc_path)
        rc, out, err = proc.command(cmd, shell=True)

        if rc is 0:
            logger.info("archive ok: {src_path} {arc_path}".format(
                src_path=src_path, arc_path=arc_path))
        else:
            logger.warn("archive failure: {src_path} {arc_path} {out} {err}".format(
                src_path=src_path, arc_path=arc_path, out=out, err=err))

    def make_arc_dir(self):

        now_ts = timeutil.ts() - time.timezone - self.time_toleration
        date_str = timeutil.format_ts(now_ts, 'daily')

        arc_dir = os.path.join(self.arc_base, date_str )
        fsutil.makedirs(arc_dir)

        symlink_path = os.path.join(self.arc_base, 'current')

        while True:
            try:
                os.symlink(arc_dir, symlink_path)
                break
            except OSError as e:
                if e[0] == errno.EEXIST:
                    os.unlink(symlink_path)
                else:
                    raise

        return arc_dir

    def make_arc_fn(self, src_path):

        src_fn = os.path.basename(src_path)
        iptag = self.ip_tag()
        arc_fn = src_fn + "." + iptag + ".gz"

        return arc_fn

    def ip_tag(self):

        ips = net.get_host_ip4()
        ips = net.ips_prefer(ips, net.INN)
        ip = (ips + [ 'x.x.x.x' ])[ 0 ]

        return ip

def archive(src_path, arc_base):

    src_dir = os.path.dirname(src_path)
    src_fn = os.path.basename(src_path)

    archiver = Archiver(src_dir, arc_base)
    archiver.archive(src_fn)

def clean(arc_base, **kwargs):

    archiver = Archiver('', arc_base, **kwargs)
    archiver.clean()
