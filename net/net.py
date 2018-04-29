import logging
import re
import socket
import struct
import sys
import types

import netifaces
import yaml

PUB = 'PUB'
INN = 'INN'

LOCALHOST = '127.0.0.1'

logger = logging.getLogger(__name__)

_intra_patterns = (
    '172\.(1[6-9]|2[0-9]|3[0-1]).*',
    '10\..*',
    '192\.168\..*',
)


class NetworkError(Exception):
    pass


class IPUnreachable(NetworkError):
    pass


class InvalidIP4(Exception):
    pass


class InvalidIP4Number(Exception):
    pass


def is_ip4(ip):

    if type(ip) not in types.StringTypes:
        return False

    ip = ip.split('.')

    for s in ip:

        if not s.isdigit():
            return False

        i = int(s)
        if i < 0 or i > 255:
            return False

    return len(ip) == 4


def ip_class(ip):

    if ip.startswith('127.0.0.'):
        return INN

    for ptn in _intra_patterns:

        if re.match(ptn, ip):
            return INN

    else:
        return PUB


def is_ip4_loopback(ip):

    return is_ip4(ip) and ip.startswith('127.')


def ips_prefer(ips, preference):

    eips = choose_pub(ips)
    iips = choose_inn(ips)

    if preference == PUB:
        return eips + iips
    else:
        return iips + eips


def is_pub(ip):
    return ip_class(ip) == PUB


def is_inn(ip):
    return ip_class(ip) == INN


def choose_pub(ips):
    return [x for x in ips if ip_class(x) == PUB]


def choose_inn(ips):
    return [x for x in ips if ip_class(x) == INN]


def get_host_ip4(iface_prefix=None, exclude_prefix=None):

    if iface_prefix is None:
        iface_prefix = ['']

    if type(iface_prefix) in types.StringTypes:
        iface_prefix = [iface_prefix]

    if exclude_prefix is not None:
        if type(exclude_prefix) in types.StringTypes:
            exclude_prefix = [exclude_prefix]

    ips = []

    for ifacename in netifaces.interfaces():

        matched = False

        for t in iface_prefix:
            if ifacename.startswith(t):
                matched = True
                break

        if exclude_prefix is not None:
            for ex in exclude_prefix:
                if ifacename.startswith(ex):
                    matched = False
                    break

        if not matched:
            continue

        addrs = netifaces.ifaddresses(ifacename)

        if netifaces.AF_INET in addrs and netifaces.AF_LINK in addrs:

            for addr in addrs[netifaces.AF_INET]:

                ip = str(addr['addr'])

                if not is_ip4_loopback(ip):
                    ips.append(ip)

    return ips


def choose_by_idc(dest_idc, local_idc, ips):

    if dest_idc == local_idc:
        pref_ips = ips_prefer(ips, INN)
    else:
        pref_ips = ips_prefer(ips, PUB)

    return pref_ips


def get_host_devices(iface_prefix=''):

    rst = {}

    for ifacename in netifaces.interfaces():

        if not ifacename.startswith(iface_prefix):
            continue

        addrs = netifaces.ifaddresses(ifacename)

        if netifaces.AF_INET in addrs and netifaces.AF_LINK in addrs:

            ips = [addr['addr'] for addr in addrs[netifaces.AF_INET]]

            for ip in ips:
                if is_ip4_loopback(ip):
                    break
            else:
                rst[ifacename] = {'INET': addrs[netifaces.AF_INET],
                                  'LINK': addrs[netifaces.AF_LINK]}

    return rst


def parse_ip_regex_str(ip_regexs_str):

    ip_regexs_str = ip_regexs_str.strip()

    regs = ip_regexs_str.split(',')
    rst = []
    for r in regs:
        # do not choose ip if it matches this regex
        if r.startswith('-'):
            r = (r[1:], False)
        else:
            r = (r, True)

        if r[0] == '':
            raise ValueError('invalid regular expression: ' + repr(r))

        if r[1]:
            r = r[0]

        rst.append(r)

    return rst


def choose_by_regex(ips, ip_regexs):

    rst = []

    for ip in ips:

        all_negative = True
        for ip_regex in ip_regexs:

            # choose matched:
            #     '127[.]'
            #     ('127[.]', True)
            # choose unmatched:
            #     ('127[.], False)

            if type(ip_regex) in (type(()), type([])):
                ip_regex, to_choose = ip_regex
            else:
                ip_regex, to_choose = ip_regex, True

            all_negative = all_negative and not to_choose

            # when to choose it:
            #     match one of positive regex.
            #     and match none of negative regex.

            if re.match(ip_regex, ip):
                if to_choose:
                    rst.append(ip)

                break
        else:
            # if all regexs are for excluding ip, then choose it
            if all_negative:
                rst.append(ip)

    return rst


def ip_to_num(ip_str):

    if not is_ip4(ip_str):
        raise InvalidIP4('IP is invalid: {s}'.format(s=ip_str))

    return struct.unpack('>L', socket.inet_aton(ip_str))[0]


def num_to_ip(ip_num):

    if isinstance(ip_num, bool) or not isinstance(ip_num, (int, long)):
        raise InvalidIP4Number('The type of IP4 number should be int or long :{t}'.format(t=type(ip_num)))
    if ip_num > 0xffffffff or ip_num < 0:
        raise InvalidIP4Number('IP4 number should be between 0 and 0xffffffff :{s}'.format(s=ip_num))

    return socket.inet_ntoa(struct.pack('>L', ip_num))


if __name__ == "__main__":

    args = sys.argv[1:]

    if args[0] == 'ip':
        print yaml.dump(get_host_ip4(), default_flow_style=False)

    elif args[0] == 'device':
        print yaml.dump(get_host_devices(), default_flow_style=False)

    else:
        raise ValueError('invalid command line arguments', args)
