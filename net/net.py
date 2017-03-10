import logging
import re
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

                ip = addr['addr']

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

    rst = ip_regexs_str.split(',')
    for r in rst:
        if r == '':
            raise ValueError('invalid regular expression: ' + repr(r))

    return rst


def choose_by_regex(ips, ip_regexs):

    rst = []

    for ip in ips:

        for ip_regex in ip_regexs:
            if re.match(ip_regex, ip):
                rst.append(ip)
                break

    return rst


if __name__ == "__main__":

    args = sys.argv[1:]

    if args[0] == 'ip':
        print yaml.dump(get_host_ip4(), default_flow_style=False)

    elif args[0] == 'device':
        print yaml.dump(get_host_devices(), default_flow_style=False)

    else:
        raise ValueError('invalid command line arguments', args)
