#!/usr/bin/env python
# coding: utf-8

from kazoo.client import KazooClient

from pykit import config
from pykit import utfjson

from . import zkutil


class ZKConf(object):

    """
    zk dir:
        <prefix>/record/<key>
        <prefix>/lock/<key>
        <prefix>/tx/
                    alive/0000000001
                    journal/0000000001
                    state/0000000001
                    txidset
                    txid_maker
        <prefix>/seq/<key>

    alive:      Contains `ephemeral` node each of which represents a transaction.
                Its modifications is used.

    journal:    Contains journal transaction modifications. Each of them is a complete transaction.

    txidset: Last committed txid number.
    """

    def __init__(self,
                 hosts=None,
                 tx_dir=None,
                 seq_dir=None,
                 record_dir=None,
                 lock_dir=None,
                 node_id=None,
                 auth=None,
                 acl=None
                 ):

        self.conf = {
            'hosts':      hosts,
            'tx_dir':     tx_dir,
            'seq_dir':    seq_dir,
            'record_dir': record_dir,
            'lock_dir':   lock_dir,
            'node_id':    node_id,
            'auth':       auth,
            'acl':        acl,
        }

    def hosts(self): return self._get_config('hosts')

    def record_dir(self): return self._get_config('record_dir')

    def lock_dir(self): return self._get_config('lock_dir')

    def node_id(self): return self._get_config('node_id')

    def auth(self): return self._get_config('auth')

    def acl(self): return self._get_config('acl')

    def lock(self, key=''): return ''.join([self.lock_dir(), _dump_txid(key)])

    def record(self, key=''): return ''.join([self.record_dir(), key])

    def seq_dir(self): return self._get_config('seq_dir')

    def seq(self, key=''): return ''.join([self.seq_dir(), key])

    def tx_dir(self): return self._get_config('tx_dir')

    def tx_alive(self, txid=''): return ''.join([self.tx_dir(), 'alive/', _dump_txid(txid)])

    def tx_state(self, txid=''): return ''.join([self.tx_dir(), 'state/', _dump_txid(txid)])

    def journal(self, txid=''): return ''.join([self.tx_dir(), 'journal/', _dump_txid(txid)])

    def txidset(self): return ''.join([self.tx_dir(), 'txidset'])

    def txid_maker(self): return ''.join([self.tx_dir(), 'txid_maker'])

    def kazoo_digest_acl(self):
        a = self.acl()
        if a is None:
            return a

        return zkutil.make_kazoo_digest_acl(a)

    def kazoo_auth(self):

        a = self.auth()
        if a is None:
            return None

        return a[0], a[1] + ':' + a[2]

    def _get_config(self, name):

        if self.conf[name] is None:
            return getattr(config, 'zk_' + name)
        else:
            return self.conf[name]


class KazooClientExt(KazooClient):

    def __init__(self, zkclient, json=True):

        if isinstance(zkclient, KazooClientExt):
            self._zk = zkclient._zk
            self._zkconf = ZKConf(**zkclient._zkconf.conf)

        elif isinstance(zkclient, KazooClient):
            self._zk = zkclient
            self._zkconf = None
        else:
            raise TypeError('invalid zkclient type: expect KazooClient or KazooClientExt')

        self._json = json

    def __getattr__(self, n):
        return getattr(self._zk, n)

    def _jl(self, v):
        if self._json:
            return utfjson.load(v)
        else:
            return v

    def _jd(self, v):
        if self._json:
            return utfjson.dump(v)
        else:
            return v

    def get(self, path, watch=None):
        val, zstat = self._zk.get(path, watch=watch)
        return self._jl(val), zstat

    def set(self, path, value, version=-1):
        value = self._jd(value)
        return self._zk.set(path, value, version=version)

    def create(self, path, value=b"", acl=None, ephemeral=False,
               sequence=False, makepath=False):

        value = self._jd(value)

        return self._zk.create(path, value=value,
                               acl=acl,
                               ephemeral=ephemeral,
                               sequence=sequence,
                               makepath=makepath)


def _dump_txid(txid):
    if isinstance(txid, str):
        return txid
    elif isinstance(txid, (int, long)):
        return '%010d' % txid
    else:
        raise TypeError('invalid type txid: ' + repr(txid))


def kazoo_client_ext(zk, json=True):
    """
    return zkclient created or original zkclient, and if zkclient is created
    """

    zkconf = None

    if isinstance(zk, str):
        zkconf = ZKConf(hosts=zk)

    if isinstance(zk, dict):
        zkconf = ZKConf(**zk)

    if isinstance(zk, ZKConf):
        zkconf = zk

    if zkconf is None:
        zkconf = ZKConf()
        owning = False
    else:
        zk = KazooClient(zkconf.hosts())
        owning = True

    zkclient = KazooClientExt(zk, json=json)
    zkclient._zkconf = zkconf

    zkclient.start()

    auth = zkconf.kazoo_auth()
    if auth is not None:
        zkclient.add_auth(*auth)

    return zkclient, owning
