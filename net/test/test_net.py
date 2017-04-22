import unittest

from pykit import ututil
from pykit import net

dd = ututil.dd

class TestNet(unittest.TestCase):

    def test_const(self):
        self.assertEqual('PUB', net.PUB)
        self.assertEqual('INN', net.INN)

        self.assertEqual('127.0.0.1', net.LOCALHOST)

    def test_exception(self):
        [net.NetworkError, net.IPUnreachable]

    def test_is_ip4_false(self):

        cases_not_ip4 = (
            None,
            True,
            False,
            1,
            0,
            '',
            '1',
            (),
            [],
            {},
            '1.',
            '1.1',
            '1.1.',
            '1.1.1',
            '1.1.1.',

            '.1.1.1',

            'x.1.1.1',
            '1.x.1.1',
            '1.1.x.1',
            '1.1.1.x',

            '1.1.1.1.',
            '.1.1.1.1',
            '1:1.1.1',
            '1:1:1.1',

            '256.1.1.1',
            '1.256.1.1',
            '1.1.256.1',
            '1.1.1.256',

            '1.1.1.1.',
            '1.1.1.1.1',
            '1.1.1.1.1.',
            '1.1.1.1.1.1',
        )

        for inp in cases_not_ip4:
            self.assertEqual(False, net.is_ip4(inp), inp)

    def test_is_ip4_true(self):

        cases_ip4 = (
            '0.0.0.0',
            '0.0.0.1',
            '0.0.1.0',
            '0.1.0.0',
            '1.0.0.0',

            '127.0.0.1',

            '255.255.255.255',
        )

        for inp in cases_ip4:
            self.assertEqual(True, net.is_ip4(inp), inp)

    def test_is_ip4_loopback_false(self):

        cases_ip4 = (
            '0.0.0.0',
            '1.1.1.1',
            '126.0.1.0',
            '15.1.0.0',
            '255.0.0.255',

            '126.0.0.1',
            '128.0.0.1',

            '255.255.255.255',
        )

        for ip in cases_ip4:
            self.assertEqual(False, net.is_ip4_loopback(ip), ip)

    def test_is_ip4_loopback_true(self):

        cases_ip4 = (
            '127.0.0.0',
            '127.1.1.1',
            '127.0.1.0',
            '127.1.0.0',
            '127.0.0.255',

            '127.0.0.1',

            '127.255.255.255',
        )

        for ip in cases_ip4:
            self.assertEqual(True, net.is_ip4_loopback(ip), ip)

    def test_ip_class_and_is_xxx(self):
        cases_pub = (
            '1.2.3.4',
            '255.255.0.0',
            '171.0.0.0',
            '173.0.0.0',
            '172.15.0.0',
            '172.32.0.0',
            '9.0.0.0',
            '11.0.0.0',
            '192.167.0.0',
            '192.169.0.0',
            '191.168.0.0',
            '193.168.0.0',
        )

        for inp in cases_pub:
            self.assertEqual(net.PUB, net.ip_class(inp), inp)

            # test is_xxx
            self.assertEqual(True, net.is_pub(inp))
            self.assertEqual(False, net.is_inn(inp))

            # test choose_xxx
            self.assertEqual([inp], net.choose_pub([inp, '192.168.0.0']))
            self.assertEqual([inp], net.choose_pub(['192.168.0.0', inp]))

        cases_inn = (
            '127.0.0.1',
            '127.0.0.255',
            '172.16.0.0',
            '172.17.0.0',
            '172.21.0.0',
            '172.30.0.0',
            '172.31.0.0',
            '10.0.0.0',
            '192.168.0.0',
        )

        for inp in cases_inn:
            self.assertEqual(net.INN, net.ip_class(inp), inp)

            # test is_xxx

            self.assertEqual(True, net.is_inn(inp))
            self.assertEqual(False, net.is_pub(inp))

            # test choose_xxx
            self.assertEqual([inp], net.choose_inn([inp, '1.1.1.1']))
            self.assertEqual([inp], net.choose_inn(['1.1.1.1', inp]))

    def test_ips_prefer(self):

        cases = (
            ([], net.PUB, []),
            ([], net.INN, []),

            (['1.2.3.4'], net.PUB, ['1.2.3.4']),
            (['1.2.3.4'], net.INN, ['1.2.3.4']),

            (['172.16.0.1'], net.PUB, ['172.16.0.1']),
            (['172.16.0.1'], net.INN, ['172.16.0.1']),

            (['172.16.0.1', '1.2.3.4'], net.PUB, ['1.2.3.4', '172.16.0.1']),
            (['172.16.0.1', '1.2.3.4'], net.INN, ['172.16.0.1', '1.2.3.4']),

            (['1.2.3.4', '172.16.0.1'], net.PUB, ['1.2.3.4', '172.16.0.1']),
            (['1.2.3.4', '172.16.0.1'], net.INN, ['172.16.0.1', '1.2.3.4']),
        )

        for inp_ips, inp_class, outp in cases:
            self.assertEqual(outp, net.ips_prefer(inp_ips, inp_class))

    def test_ips_prefer_by_idc(self):
        cases = (
            ('a', 'a', [], []),
            ('a', 'a', ['1.1.1.1'], ['1.1.1.1']),
            ('a', 'a', ['172.16.0.0'], ['172.16.0.0']),
            ('a', 'a', ['172.16.0.0', '1.1.1.1'], ['172.16.0.0', '1.1.1.1']),
            ('a', 'a', ['1.1.1.1', '172.16.0.0'], ['172.16.0.0', '1.1.1.1']),

            ('a', 'b', [], []),
            ('a', 'b', ['1.1.1.1'], ['1.1.1.1']),
            ('a', 'b', ['172.16.0.0'], ['172.16.0.0']),
            ('a', 'b', ['172.16.0.0', '1.1.1.1'], ['1.1.1.1', '172.16.0.0']),
            ('a', 'b', ['1.1.1.1', '172.16.0.0'], ['1.1.1.1', '172.16.0.0']),
        )

        for idc_a, idc_b, ips, outp in cases:
            self.assertEqual(outp, net.choose_by_idc(idc_a, idc_b, ips))

    def test_get_host_ip4(self):

        ips = net.get_host_ip4(iface_prefix='')
        self.assertNotEqual([], ips)

        ips2 = net.get_host_ip4(exclude_prefix='')
        self.assertEqual([], ips2, 'exclude any')

        self.assertEqual(ips, net.get_host_ip4(
            exclude_prefix=[]), 'exclude nothing')

        self.assertEqual(ips, net.get_host_ip4(
            exclude_prefix=None), 'exclude nothing')

    def test_get_host_devices(self):
        # TODO can not test
        net.get_host_devices(iface_prefix='')

    def test_parse_ip_regex_str(self):

        cases = (
            ('1.2.3.4',        ['1.2.3.4']),
            ('1.2.3.4,127.0.', ['1.2.3.4', '127.0.']),
            ('-1.2.3.4,127.0.', [('1.2.3.4', False), '127.0.']),
            ('-1.2.3.4,-127.0.', [('1.2.3.4', False), ('127.0.', False)]),
        )

        for inp, outp in cases:
            self.assertEqual(outp, net.parse_ip_regex_str(inp))

        cases_err = (
            '',
            ',',
            ' , ',
            '1,',
            ',1',
            '-1,',
            ',-1',
            '127,-',
            '-,127',
        )
        for inp in cases_err:

            dd('should fail with: ', repr(inp))

            try:
                net.parse_ip_regex_str(inp)
                self.fail('should fail with ' + repr(inp))
            except ValueError:
                pass

    def test_choose_ips_regex(self):
        cases = (
            (['127.0.0.1', '192.168.0.1'], ['127[.]'],
             ['127.0.0.1']),

            (['127.0.0.1', '192.168.0.1'], ['2'],
             []),

            (['127.0.0.1', '192.168.0.1'], ['[.]'],
             []),

            (['127.0.0.1', '192.168.0.1'], ['1'],
             ['127.0.0.1', '192.168.0.1']),

            # negative match
            (['127.0.0.1', '192.168.0.1'], [('1', False)],
             []),

            (['127.0.0.1', '192.168.0.1'], [('127', False), ('192', False)],
             []),

            (['127.0.0.1', '192.168.0.1'], [('12', False)],
             ['192.168.0.1']),

            (['127.0.0.1', '192.168.0.1'], ['22', ('12', False)],
             []),
        )

        for ips, regs, outp in cases:
            dd('case: ', ips, regs, outp)
            self.assertEqual(outp, net.choose_by_regex(ips, regs))
