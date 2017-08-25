#!/usr/bin/env python2
# coding: utf-8

import time
import unittest

from pykit import etcd
from pykit import utdocker
from pykit import utfjson
from pykit import ututil

dd = ututil.dd

HOSTS = (
    ("192.168.52.30", 3379),
    ("192.168.52.31", 3379),
    ("192.168.52.32", 3379),
    ("192.168.52.33", 3379),
    ("192.168.52.34", 3379),
)

ETCD_NAMES = ('etcd_t0', 'etcd_t1', 'etcd_t2', 'etcd_t3', 'etcd_t4',)
ETCD_NODES = ('node_0', 'node_1', 'node_2', 'node_3', 'node_4',)

etcd_test_tag = 'quay.io/coreos/etcd:v2.3.7'


class TestEtcdKeysResult(unittest.TestCase):

    def test_get_subtree_1_level(self):

        response = {"node": {
            'key': "/test",
            'value': "hello",
            'expiration': None,
            'ttl': None,
            'modifiedIndex': 5,
            'createdIndex': 1,
            'newKey': False,
            'dir': False,
        }}
        result = etcd.EtcdKeysResult(**response)
        for k, v in response['node'].items():
            self.assertEqual(v, getattr(result, k))

        self.assertListEqual([result], list(
            result.get_subtree(leaves_only=False)))
        self.assertListEqual([result], list(
            result.get_subtree(leaves_only=True)))
        self.assertListEqual([result], list(result.leaves))

    def test_get_subtree_2_level(self):

        leaf0 = {
            'key': "/test/leaf0",
            'value': "hello1",
            'expiration': None,
            'ttl': None,
            'modifiedIndex': 5,
            'createdIndex': 1,
            'newKey': False,
            'dir': False,
        }
        leaf1 = {
            'key': "/test/leaf1",
            'value': "hello2",
            'expiration': None,
            'ttl': None,
            'modifiedIndex': 6,
            'createdIndex': 2,
            'newKey': False,
            'dir': False,
        }
        testnode = {"node": {
            'key': "/test/",
            'expiration': None,
            'ttl': None,
            'modifiedIndex': 6,
            'createdIndex': 2,
            'newKey': False,
            'dir': True,
            'nodes': [leaf0, leaf1]
        }}
        result = etcd.EtcdKeysResult(**testnode)
        for k, v in testnode['node'].items():
            if not hasattr(result, k):
                continue

            self.assertEqual(v, getattr(result, k))

        self.assertListEqual(result._children, testnode['node']['nodes'])

        subtree = list(result.get_subtree(leaves_only=True))
        self.assertEqual("/test/leaf0", subtree[0].key)
        self.assertEqual("/test/leaf1", subtree[1].key)
        self.assertEqual(len(subtree), 2)
        self.assertListEqual(subtree, list(result.leaves))

        subtree = list(result.get_subtree(leaves_only=False))
        self.assertEqual("/test/", subtree[0].key)
        self.assertEqual("/test/leaf0", subtree[1].key)
        self.assertEqual("/test/leaf1", subtree[2].key)
        self.assertEqual(len(subtree), 3)

    def test_get_subtree_3_level(self):

        leaf0 = {
            'key': "/test/mid0/leaf0",
            'value': "hello1",
        }
        leaf1 = {
            'key': "/test/mid0/leaf1",
            'value': "hello2",
        }
        leaf2 = {
            'key': "/test/mid1/leaf2",
            'value': "hello1",
        }
        leaf3 = {
            'key': "/test/mid1/leaf3",
            'value': "hello2",
        }
        mid0 = {
            'key': "/test/mid0/",
            'dir': True,
            'nodes': [leaf0, leaf1]
        }
        mid1 = {
            'key': "/test/mid1/",
            'dir': True,
            'nodes': [leaf2, leaf3]
        }
        testnode = {"node": {
            'key': "/test/",
            'dir': True,
            'nodes': [mid0, mid1]
        }}

        result = etcd.EtcdKeysResult(**testnode)
        for k, v in testnode['node'].items():
            if not hasattr(result, k):
                continue

            self.assertEqual(v, getattr(result, k))

        self.assertListEqual(result._children, testnode['node']['nodes'])

        subtree = list(result.get_subtree(leaves_only=True))
        self.assertEqual("/test/mid0/leaf0", subtree[0].key)
        self.assertEqual("/test/mid0/leaf1", subtree[1].key)
        self.assertEqual("/test/mid1/leaf2", subtree[2].key)
        self.assertEqual("/test/mid1/leaf3", subtree[3].key)
        self.assertEqual(len(subtree), 4)
        self.assertListEqual(subtree, list(result.leaves))

        subtree = list(result.get_subtree(leaves_only=False))
        self.assertEqual("/test/", subtree[0].key)
        self.assertEqual("/test/mid0/", subtree[1].key)
        self.assertEqual("/test/mid0/leaf0", subtree[2].key)
        self.assertEqual("/test/mid0/leaf1", subtree[3].key)
        self.assertEqual("/test/mid1/", subtree[4].key)
        self.assertEqual("/test/mid1/leaf2", subtree[5].key)
        self.assertEqual("/test/mid1/leaf3", subtree[6].key)
        self.assertEqual(len(subtree), 7)

    def test_eq_ne(self):

        cases = (
            ({'node': {'key': 'key1'}},
             {'node': {'key': 'key2'}},
             False,
             ),

            ({'node': {'key': 'key1'}},
             {'node': {'key': 'key1'}},
             True,
             ),

            ({'node': {'key': 'key1', 'value': 'val1'}},
             {'node': {'key': 'key1', 'value': 'val2'}},
             False,
             ),
        )

        for node1, node2, expected_res in cases:
            res1 = etcd.EtcdKeysResult(**node1)
            res2 = etcd.EtcdKeysResult(**node2)
            self.assertEqual(res1 == res2, expected_res)


class TestException(unittest.TestCase):

    def test_errorcode_exception(self):

        cases = (
            ({'errorCode': 100, 'message': 'foo', 'cause': 'bar'},
             etcd.EcodeKeyNotFound, 'foo : bar'),

            ({'errorCode': 101, 'message': 'foo', 'cause': 'bar'},
             etcd.EcodeTestFailed, 'foo : bar'),

            ({'errorCode': 102, 'message': 'foo', 'cause': 'bar'},
             etcd.EcodeNotFile, 'foo : bar'),

            ({'errorCode': 103, 'message': 'foo', 'cause': 'bar'},
             etcd.EtcdException, 'foo : bar'),

            ({'errorCode': 104, 'message': 'foo', 'cause': 'bar'},
             etcd.EcodeNotDir, 'foo : bar'),

            ({'errorCode': 105, 'message': 'foo', 'cause': 'bar'},
             etcd.EcodeNodeExist, 'foo : bar'),

            ({'errorCode': 106, 'message': 'foo', 'cause': 'bar'},
             etcd.EtcdKeyError, 'foo : bar'),

            ({'errorCode': 107, 'message': 'foo', 'cause': 'bar'},
             etcd.EcodeRootROnly, 'foo : bar'),

            ({'errorCode': 108, 'message': 'foo', 'cause': 'bar'},
             etcd.EcodeDirNotEmpty, 'foo : bar'),

            ({'errorCode': 110, 'message': 'foo', 'cause': 'bar'},
             etcd.EcodeInscientPermissions, 'foo : bar'),

            ({'errorCode': 200, 'message': 'foo', 'cause': 'bar'},
             etcd.EtcdValueError, 'foo : bar'),

            ({'errorCode': 201, 'message': 'foo', 'cause': 'bar'},
             etcd.EcodePrevValueRequired, 'foo : bar'),

            ({'errorCode': 202, 'message': 'foo', 'cause': 'bar'},
             etcd.EcodeTTLNaN, 'foo : bar'),

            ({'errorCode': 203, 'message': 'foo', 'cause': 'bar'},
             etcd.EcodeIndexNaN, 'foo : bar'),

            ({'errorCode': 209, 'message': 'foo', 'cause': 'bar'},
             etcd.EcodeInvalidField, 'foo : bar'),

            ({'errorCode': 210, 'message': 'foo', 'cause': 'bar'},
             etcd.EcodeInvalidForm, 'foo : bar'),

            ({'errorCode': 300, 'message': 'foo', 'cause': 'bar'},
             etcd.EtcdInternalError, 'foo : bar'),

            ({'errorCode': 301, 'message': 'foo', 'cause': 'bar'},
             etcd.EtcdInternalError, 'foo : bar'),

            ({'errorCode': 400, 'message': 'foo', 'cause': 'bar'},
             etcd.EtcdWatchError, 'foo : bar'),

            ({'errorCode': 401, 'message': 'foo', 'cause': 'bar'},
             etcd.EtcdWatchError, 'foo : bar'),

            ({'errorCode': 500, 'message': 'foo', 'cause': 'bar'},
             etcd.EtcdInternalError, 'foo : bar'),

            ({'errorCode': 501, 'message': 'foo', 'cause': 'bar'},
             etcd.EtcdException, 'Unable to decode server response'),

            ({},
             etcd.EtcdException, 'Unable to decode server response'),
        )

        for res_body, e, expect_msg in cases:
            res = etcd.Response(body=utfjson.dump(res_body))
            self.assertRaisesRegexp(e, expect_msg, etcd.EtcdError.handle, res)


class TestClient(unittest.TestCase):

    def setUp(self):
        _start_etcd_server(HOSTS, ETCD_NAMES, ETCD_NODES)
        self._clear_all()

    def _clear_all(self):

        while True:
            try:
                c = etcd.Client(host=HOSTS)
                res = c.get('', recursive=True)
                for n in res._children:
                    c.delete(n['key'], dir='dir' in n and n['dir'],
                             recursive=True)
                break
            except Exception as e:
                dd(repr(e))
                time.sleep(1)

    def test_machine_cache(self):

        machine = list(HOSTS)
        machine.pop(0)
        machine = ['http://%s:%d' % (ip, port) for ip, port in machine]
        cases = (
            (HOSTS, 3379, True, machine),
            ('192.168.52.30', 3379, True, machine),
            (HOSTS, 3379, False, []),
            ('192.168.52.30', 3379, False, []),
        )

        for host, port, allow_reconnect, expected_machines in cases:
            c = etcd.Client(host=host, port=port,
                            allow_reconnect=allow_reconnect)
            self.assertEqual('http://192.168.52.30:3379', c._base_uri)
            self.assertListEqual(expected_machines, c._machines_cache)

    def test_property(self):

        cases = (
            ('192.168.52.30', 3379, 'http', 10, True),
            ('192.168.52.31', 3379, 'http', 20, False),
        )

        for host, port, protocol, timeout, allow_redirect in cases:
            c = etcd.Client(host=host, port=port, protocol=protocol,
                            read_timeout=timeout, allow_redirect=allow_redirect)
            self.assertEqual(host, c.host)
            self.assertEqual(port, c.port)
            self.assertEqual(protocol, c.protocol)
            self.assertEqual(timeout, c.read_timeout)
            self.assertEqual(allow_redirect, c.allow_redirect)
            self.assertEqual('%s://%s:%d' % (protocol, host, port), c.base_uri)

    def test_members(self):

        c = etcd.Client(host=HOSTS)

        mems = c.members
        for h, p in HOSTS:
            succ = False
            for m in mems:
                if 'http://%s:%d' % (h, p) == m['clientURLs'][0]:
                    succ = True
                    break
            self.assertTrue(succ)

    def test_leader(self):

        c = etcd.Client(host=HOSTS)

        leader = c.leader
        self.assertIsNotNone(leader)
        self.assertIn(leader, c.members)

    def test_version(self):

        c = etcd.Client(host=HOSTS)

        ver = c.version
        self.assertIn('etcdserver', ver)
        self.assertIn('etcdcluster', ver)

    def test_nomoremachine_exception(self):

        utdocker.stop_container(*ETCD_NAMES)
        c = etcd.Client(host=HOSTS, read_timeout=1)
        self.assertRaises(etcd.NoMoreMachineError, c.get, '/key')

    def test_etcdreadtimeouterror_exception(self):

        utdocker.stop_container(*ETCD_NAMES)
        c = etcd.Client(host=HOSTS, read_timeout=1)
        self.assertRaises(etcd.EtcdReadTimeoutError, c.api_execute,
                          '/v2/keys/abc', 'GET', timeout=1,
                          raise_read_timeout=True)

    def test_etcdrequestserror_exception(self):

        c = etcd.Client(host=HOSTS)
        self.assertRaises(etcd.EtcdRequestError, c._request,
                          'http://192.168.52.30:3379/v2/keys/abc',
                          'GETTT', None, None, None)
        self.assertRaises(etcd.EtcdRequestError, c.write,
                          dir=True, value='val', key='key')

    def test_etcdincompleteread_exception(self):

        res = etcd.Response(body='abc')
        c = etcd.Client(host=HOSTS)
        self.assertRaises(etcd.EtcdIncompleteRead,
                          c._to_dict, res)

    def test_etcdsslerror_exception(self):

        c = etcd.Client(host=HOSTS)
        self.assertRaises(etcd.EtcdSSLError, etcd.Client,
                          host=HOSTS, protocol='https')
        self.assertRaises(etcd.EtcdSSLError,
                          c._parse_url, 'https://')

    def test_next_server(self):

        utdocker.stop_container('etcd_t0')
        c = etcd.Client(host=HOSTS, read_timeout=2)
        c.set('key', 'val')
        self.assertIn('key', c)

    def test_set_and_get(self):

        cases = (
            ('foo', 'f'),
            ('123', '456'),
            ('12foo', '1f'),
            ('*-@', 'special'),

            ('/bar', 'bb'),
            ('/789', '1000'),
            ('/12bar', '1bb'),
            ('/$*-', 'specialss'),
        )

        cli = etcd.Client(host=HOSTS)
        for key, val in cases:
            cli.set(key, val)
            res = cli.get(key)
            self.assertEqual(val, res.value)

    def test_decode(self):

        cases = (
            ('key1', utfjson.dump(u'我', encoding=None), '"\\u6211"'),

            # when save '"\xb6\xd4"' with etcd but the etcd cannot
            # convert them, so the default '\ufffd\ufffd' was saved.
            # when get it from etcd, '\ufffd\ufffd' was converted into
            # '"\xef\xbf\xbd\xef\xbf\xbd"'.
            ('key2', utfjson.dump(u'对', encoding='gbk'),
             '"\xef\xbf\xbd\xef\xbf\xbd"'),

            ('key3', utfjson.dump(u'我', encoding='utf-8'), '"\xe6\x88\x91"'),

            ('key4', utfjson.dump(u'我'), '"\xe6\x88\x91"'),
            ('key5', utfjson.dump('我'), '"\xe6\x88\x91"'),

            ('key6', utfjson.dump({"我": "我"}),
             '{"\xe6\x88\x91": "\xe6\x88\x91"}'),

            ('key7', utfjson.dump({"我": u"我"}),
             '{"\xe6\x88\x91": "\xe6\x88\x91"}'),

            ('key8', utfjson.dump({u"我": "我"}),
             '{"\xe6\x88\x91": "\xe6\x88\x91"}'),

            ('key9', utfjson.dump({u"我": u"我"}),
             '{"\xe6\x88\x91": "\xe6\x88\x91"}'),

            ('key10', utfjson.dump((u"我",)), '["\xe6\x88\x91"]'),
        )

        cli = etcd.Client(host=HOSTS)
        for key, val, expected in cases:
            cli.set(key, val)
            res = cli.get(key)
            self.assertEqual(expected, res.value)

    def test_ttl(self):

        c = etcd.Client(host=HOSTS)

        c.set('abc', 'val', ttl=1)
        self.assertIn('abc', c)
        time.sleep(2)
        self.assertNotIn('abc', c)

    def test_get_conditions(self):

        c = etcd.Client(host=HOSTS)

        kv = (
            ('key1', 'val1', False),
            ('key2', 'val2', False),
            ('dir1', None, True),
            ('dir1/key3', 'val3', False),
        )
        for k, v, d in kv:
            c.test_and_set(k, v, dir=d)

        nodes = c.get('', sorted=True)._children
        self.assertEqual('/dir1', nodes[0]['key'])
        self.assertEqual('/key1', nodes[1]['key'])
        self.assertEqual('/key2', nodes[2]['key'])

        nodes = c.get('', sorted=True, recursive=False)._children
        self.assertNotIn('nodes', nodes[0])
        nodes = c.get('', sorted=True, recursive=True)._children
        self.assertIn('nodes', nodes[0])

    def test_set_conditions(self):

        c = etcd.Client(host=HOSTS)

        c.test_and_set('foo', 'val')
        c.test_and_set('foo', 'val', prevExist=True)
        self.assertRaises(etcd.EcodeNodeExist, c.test_and_set,
                          'foo', 'val', prevExist=False)

        res = c.test_and_set('foo', 'val1', prevValue='val')
        self.assertEqual('val1', res.value)
        self.assertRaises(etcd.EcodeTestFailed, c.test_and_set,
                          'foo', 'val1', prevValue='val1000')

        res = c.test_and_set('foo', 'val2', prevIndex=res.modifiedIndex)
        self.assertEqual('val2', res.value)

        res = c.test_and_set('foo', None, refresh=True, ttl=2)
        self.assertEqual(2, res.ttl)

    def test_set_append(self):

        c = etcd.Client(host=HOSTS)

        c.test_and_set('dd', None, dir=True)
        c.test_and_set('dd', 'val1', append=True)
        c.test_and_set('dd', 'val2', append=True)

        res = c.get('dd')
        self.assertEqual(2, len(res._children))
        for n in res.leaves:
            self.assertIn(n.value, ['val1', 'val2'])

    def test_watch(self):

        c = etcd.Client(host=HOSTS)

        res = c.set('abc', 'val')
        self.assertEqual(res.value, c.watch(
            'abc', waitindex=res.modifiedIndex).value)
        self.assertRaises(etcd.EtcdReadTimeoutError, c.watch,
                          'abc', waitindex=res.modifiedIndex + 1, timeout=1)

        start_index = res.modifiedIndex
        for i in range(4):
            res = c.set('abc', 'val%d' % (i))
            end_index = res.modifiedIndex

        result = []
        for res in c.eternal_watch('abc', waitindex=start_index + 1,
                                   until=end_index):
            result.append(res.value)

        self.assertListEqual(['val0', 'val1', 'val2', 'val3'], result)

    def test_update(self):

        c = etcd.Client(host=HOSTS)

        res = c.set('key', 'val')
        res.value += 'abc'
        res = c.update(res)

        self.assertEqual('valabc', res.value)

    def test_delete(self):

        c = etcd.Client(host=HOSTS)
        kv = (
            ('key1', 'val1', False),
            ('dir1', None, True),
            ('dir1/key2', 'val2', False),
        )
        for k, v, d in kv:
            c.test_and_set(k, v, dir=d)

        c.delete('key1')
        self.assertNotIn('key1', c)

        self.assertRaises(etcd.EcodeNotFile, c.delete, 'dir1')
        self.assertRaises(etcd.EcodeDirNotEmpty, c.delete, 'dir1', dir=True)

        c.delete('dir1', recursive=True, dir=True)
        self.assertNotIn('dir1', c)

    def test_mkdir(self):

        c = etcd.Client(host=HOSTS)

        res = c.mkdir('d')
        self.assertTrue(res.dir)
        self.assertEqual('/d', res.key)
        self.assertIn('d', c)

    def test_refresh(self):

        c = etcd.Client(host=HOSTS)

        c.set('key', 'val')
        res = c.refresh('key', ttl=1)
        self.assertEqual(1, res.ttl)

    def test_lsdir(self):

        c = etcd.Client(host=HOSTS)

        c.test_and_set('dir1', None, dir=True)
        res = c.lsdir('dir1')
        self.assertTrue(res.dir)
        self.assertEqual('/dir1', res.key)

    def test_rlsdir(self):

        c = etcd.Client(host=HOSTS)

        c.test_and_set('dir1', None, dir=True)
        c.test_and_set('dir1/key', 'val')
        res = c.rlsdir('dir1')
        self.assertTrue(res.dir)
        self.assertEqual('/dir1', res.key)
        self.assertEqual(1, len(res._children))
        self.assertEqual('val', res._children[0]['value'])

    def test_deldir(self):

        c = etcd.Client(host=HOSTS)

        c.test_and_set('dir1', None, dir=True)
        c.deldir('dir1')
        self.assertNotIn('dir1', c)

    def test_rdeldir(self):

        c = etcd.Client(host=HOSTS)

        c.test_and_set('dir1', None, dir=True)
        c.test_and_set('dir1/key', 'val')
        c.rdeldir('dir1')
        self.assertNotIn('dir1', c)

    def _set_auth(self, hosts):

        root_pwd = '123456'
        c = etcd.Client(host=hosts)
        c.create_root(root_pwd)
        c.enable_auth(root_pwd)
        c.revoke_role_permissions(
            'guest', root_pwd, {"write": ["/*"], "read": ["/*"]})
        c.create_role('rw_role', root_pwd, {"write": ["/*"], "read": ["/*"]})
        c.create_user('rw_user', '654321', root_pwd, ["rw_role"])
        time.sleep(1)

    def test_auth(self):

        hosts = (
            ('192.168.52.90', 3379),
            ('192.168.52.91', 3379),
            ('192.168.52.92', 3379),
        )
        names = ('etcd_au0', 'etcd_au1', 'etcd_au2',)
        nodes = ('node_au0', 'node_au1', 'node_au2',)
        _start_etcd_server(hosts, names, nodes)
        time.sleep(10)

        try:
            self._set_auth(hosts)
            c = etcd.Client(host=hosts)
            self.assertRaises(etcd.EcodeInscientPermissions,
                              c.set, 'key', 'val')
            self.assertRaises(etcd.EcodeInscientPermissions, c.get, '')

            c = etcd.Client(
                host=hosts, basic_auth_account='rw_user:654321')
            c.set('key', 'val')
            self.assertIn('key', c)
            res = c.get('key')
            self.assertEqual('val', res.value)

            c.disable_auth('123456')
            c = etcd.Client(host=hosts)
            c.set('key1', 'val1')
            self.assertIn('key1', c)
            res = c.get('key1')
            self.assertEqual('val1', res.value)
        finally:
            utdocker.remove_container(*names)

    def test_st_leader(self):

        c = etcd.Client(host=HOSTS)
        leader = c.st_leader
        self.assertIn('leader', leader)
        self.assertEqual(4, len(leader['followers']))

    def test_st_store(self):

        c = etcd.Client(host=HOSTS)
        store = c.st_store

        expected_res = [
            'getsSuccess',
            'getsFail',
            'setsSuccess',
            'setsFail',
            'deleteSuccess',
            'deleteFail',
            'updateSuccess',
            'updateFail',
            'createSuccess',
            'createFail',
            'compareAndSwapSuccess',
            'compareAndSwapFail',
            'compareAndDeleteSuccess',
            'compareAndDeleteFail',
            'expireCount',
            'watchers',
        ]

        self.assertEqual(set(expected_res), set(store.keys()))

    def test_st_self(self):

        c = etcd.Client(host=HOSTS)
        s = c.st_self

        self.assertTrue(type(s) is dict)
        self.assertTrue(len(s) > 0)

    def test_exception(self):

        c = etcd.Client(host=HOSTS)
        self.assertRaises(etcd.EcodeKeyNotFound, c._st, '/XXX')

    def test_names(self):

        c = etcd.Client(host=HOSTS)
        expected_res = [
            'node_0',
            'node_1',
            'node_2',
            'node_3',
            'node_4',
        ]

        self.assertEqual(set(expected_res), set(c.names))

    def test_ids(self):

        c = etcd.Client(host=HOSTS)
        self.assertEqual(5, len(c.ids))

    def test_clienturls(self):

        expected_res = ['http://%s:%d' % (ip, port) for ip, port in HOSTS]
        c = etcd.Client(host=HOSTS)
        self.assertEqual(set(expected_res), set(c.clienturls))

    def test_peerurls(self):

        expected_res = ['http://%s:3380' % (ip) for ip, _ in HOSTS]
        c = etcd.Client(host=HOSTS)
        self.assertEqual(set(expected_res), set(c.peerurls))

    def test_change_peerurls(self):

        c = etcd.Client(host=HOSTS)
        mem = c.members[0]
        old_urls = mem['peerURLs']
        new_urls = [old_urls[0] + '1']

        c.change_peerurls(mem['id'], *new_urls)
        self.assertIn(new_urls[0], c.peerurls)

        c.change_peerurls(mem['id'], *old_urls)
        self.assertIn(old_urls[0], c.peerurls)

        self.assertRaises(etcd.EtcdException, c.change_peerurls, mem['id'], [])

    def test_del_member(self):

        hosts = (
            ('192.168.52.50', 3379),
            ('192.168.52.51', 3379),
            ('192.168.52.52', 3379),
        )
        names = ('etcd_d0', 'etcd_d1', 'etcd_d2')
        nodes = ('node_d0', 'node_d1', 'node_d2',)
        _start_etcd_server(hosts, names, nodes)

        time.sleep(10)
        c = etcd.Client(host=hosts, read_timeout=1)

        try:
            for i in range(2):
                ids = c.ids
                c.del_member(ids[0])
                self.assertEqual(2 - i, len(c.members))
                time.sleep(10)
        finally:
            utdocker.remove_container(*names)

    def test_add_member(self):

        hosts = [
            ('192.168.52.70', 3379),
            ('192.168.52.71', 3379),
        ]
        names = ['etcd_a0', 'etcd_a1']
        nodes = ['node_a0', 'node_a1']
        _start_etcd_server(hosts, names, nodes)
        time.sleep(10)

        cases = (
            ('192.168.52.72', 'etcd_a2', 'node_a2', 3),
            ('192.168.52.73', 'etcd_a3', 'node_a3', 4),
        )

        c = etcd.Client(host=hosts)
        try:
            for ip, name, node, count in cases:
                c.add_member(*['http://%s:3380' % (ip)])
                hosts.append((ip, 3379))
                nodes.append(node)
                names.append(name)

                utdocker.start_container(name, etcd_test_tag, ip,
                                         _generate_command(
                                             len(hosts) - 1,
                                             hosts,
                                             nodes,
                                             state='existing'))

                time.sleep(10)

                self.assertEqual(count, len(c.members))
        finally:
            utdocker.remove_container(*names)

    def _clear_users_roles(self, root_pwd):

        c = etcd.Client(host=HOSTS)

        users = c.get_user(None, root_pwd)
        if users is not None and users['users'] is not None:
            for u in users['users']:
                try:
                    c.delete_user(u['user'], root_pwd)
                except:
                    continue

        roles = c.get_role(None, root_pwd)
        if roles is not None and roles['roles'] is not None:
            for r in roles['roles']:
                try:
                    c.delete_role(r['role'], root_pwd)
                except:
                    continue

    def test_create_root(self):

        c = etcd.Client(host=HOSTS)
        res = c.create_root('123')

        self.assertEqual('root', res['user'])

    def test_create_and_get_user(self):

        c = etcd.Client(host=HOSTS)

        cases = (
            ('u1', 'p1'),
            ('u2', 'p2'),
            ('u3', 'p3'),
            ('u4', 'p4'),
        )

        all_users = {'users': []}
        try:
            for u, p in cases:
                c.create_user(u, p, '')
                res = c.get_user(u, '')
                self.assertEqual({'user': u}, res)

                all_users['users'].append(res)
                res = c.get_user(None, '')
                self.assertEqual(all_users, res)
        finally:
            self._clear_users_roles('')

    def test_create_and_get_role(self):

        c = etcd.Client(host=HOSTS)

        cases = ('r1', 'r2', 'r3', 'r4')

        # default role cannot delete
        all_roles = [
            {'role': 'root',
             'permissions': {'kv': {'read': ['/*'], 'write': ['/*']}}}
        ]

        try:
            for r in cases:
                c.create_role(r, '')
                res = c.get_role(r, '')
                expected = {
                    'role': r,
                    'permissions': {'kv': {'read': None, 'write': None}}
                }
                self.assertEqual(expected, res)

                all_roles.insert(-1, res)
                res = c.get_role(None, '')
                self.assertEqual(all_roles, res['roles'])
        finally:
            self._clear_users_roles('')

    def test_grant_revoke_user_roles(self):

        c = etcd.Client(host=HOSTS)
        c.create_user('u_test', '11', '')
        c.create_role('r_test', '')

        try:
            c.grant_user_roles('u_test', '', ['r_test'])
            res = c.get_user('u_test', '')
            self.assertEqual('r_test', res['roles'][0]['role'])

            c.revoke_user_roles('u_test', '', ['r_test'])
            res = c.get_user('u_test', '')
            self.assertNotIn('roles', res)
        finally:
            self._clear_users_roles('')

    def test_grant_revoke_role_permissions(self):

        c = etcd.Client(host=HOSTS)
        c.create_role('r_test', '')

        try:
            c.grant_role_permissions('r_test', '', {'read': ['/*']})
            r = c.get_role('r_test', '')
            self.assertEqual(['/*'], r['permissions']['kv']['read'])

            c.revoke_role_permissions('r_test', '', {'read': ['/*']})
            r = c.get_role('r_test', '')
            self.assertEqual([], r['permissions']['kv']['read'])
        finally:
            self._clear_users_roles('')


def _generate_command(index, hosts, nodes, state='new'):

    node = nodes[index]
    ip, _ = hosts[index]
    cluster = ''
    for i in range(len(hosts)):
        cluster += '%s=http://%s:3380,' % (nodes[i], hosts[i][0])

    cluster = cluster[:-1]

    return "--name {name} \
           --initial-advertise-peer-urls http://{ip_peer_adv}:3380 \
           --listen-peer-urls http://{ip_peer}:3380 \
           --advertise-client-urls http://{ip_cli_adv}:3379 \
           --listen-client-urls http://{ip_cli}:3379 \
           --initial-cluster {cluster} \
           --initial-cluster-state {state} \
           --initial-cluster-token test_etcd_token" \
           .format(name=node, ip_peer_adv=ip, ip_peer=ip,
                   ip_cli_adv=ip, ip_cli=ip, cluster=cluster, state=state)


def _start_etcd_server(hosts, names, nodes, state='new'):

    utdocker.create_network()

    for i in range(len(hosts)):

        name = names[i]
        ip, _ = hosts[i]
        command = _generate_command(i, hosts, nodes, state=state)

        utdocker.start_container(name, etcd_test_tag, ip, command)
