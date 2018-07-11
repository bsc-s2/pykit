<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Constants](#constants)
  - [net.INN](#netinn)
  - [net.PUB](#netpub)
- [Exceptions](#exceptions)
  - [net.NetworkError](#netnetworkerror)
  - [net.IPUnreachable](#netipunreachable)
- [Methods](#methods)
  - [net.choose_by_idc](#netchoose_by_idc)
  - [net.choose_by_regex](#netchoose_by_regex)
  - [net.choose_inn](#netchoose_inn)
  - [net.choose_pub](#netchoose_pub)
  - [net.get_host_devices](#netget_host_devices)
  - [net.get_host_ip4](#netget_host_ip4)
  - [net.ip_class](#netip_class)
  - [net.ips_prefer](#netips_prefer)
  - [net.is_inn](#netis_inn)
  - [net.is_pub](#netis_pub)
  - [net.is_ip4](#netis_ip4)
  - [net.parse_ip_regex_str](#netparse_ip_regex_str)
  - [net.ip_to_num](#netip_to_num)
  - [net.num_to_ip](#netnum_to_ip)
- [Commandline Tool](#commandline-tool)
  - [ip](#ip)
  - [devcie](#devcie)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

net

#   Status

This library is considered stable for internal use only.

#   Description

Utility functions for network related operation.


#   Constants


##  net.INN

**syntax**:
`net.INN`

It is string "INN" that represents a internal ip.


##  net.PUB

**syntax**:
`net.PUB`

It is string "PUB" that represents a public ip.


# Exceptions


## net.NetworkError

**syntax**:
`net.NetworkError`

Super class of all network exceptions.


##  net.IPUnreachable

**syntax**:
`net.IPUnreachable`

Exception for an unreachable ip.


#   Methods


##  net.choose_ips

**syntax**:
`net.choose_ips(ips, ip_type=None)`

**arguments**:

-   `ips`:
    is a list of ips to choose from.

-   `ip_type`:

    - `net.PUB`: returns a list of public ip from `ips`.
    - `net.INN`: returns a list of internal ip from `ips`.
    - `None`: returns the original list.
    - Other value: raise `ValueError`.

**return**:
list of chosen ips.


##  net.choose_by_idc

**syntax**:
`net.choose_by_idc(dest_idc, my_idc, ip_list)`

Return a new list with all public ips in `ip_list`, if `dest_idc` is not
`my_idc`.

Return a new list with all internal ips in `ip_list`, if `dest_idc` is
`my_idc`.

**arguments**:

-   `dest_idc`:
    is a string representing an IDC where the ips in `ip_list` is.

-   `my_idc`:
    is a string representing the IDC where the function is running.

-   `ip_list`:
    is a list of ip in the `dest_idc`.

**return**:
a list of sub set of `ip_list`.


##  net.choose_by_regex

**syntax**:
`net.choose_by_regex(ip_list, regex_list)`

It returns a sub set list of `ip_list`.
Each ip in the result list matches at least one of the regex-es from
`regex_list`.

**arguments**:

-   `ip_list`:
    is a list of ipv4 addresses.
    See `net.parse_ip_regex_str`.

-   `regex_list`:
    is a list of regex.

**return**:
a list of ipv4 addresses, in which every ip matches at least one regex from
`regex_list`.


##  net.choose_inn

**syntax**:
`net.choose_inn(ip_list)`

Return a list of all internal ip from `ip_list`.

**arguments**:

-   `ip_list`:
    is a list of ipv4 addresses.

**return**:
a list of internal ipv4 addresses.


##  net.choose_pub

**syntax**:
`net.choose_pub(ip_list)`

Return a list of all public ip from `ip_list`.

**arguments**:

-   `ip_list`:
    is a list of ipv4 addresses.

**return**:
a list of public ipv4 addresses.


##  net.get_host_devices

**syntax**:
`net.get_host_devices(iface_prefix='')`

Returns a dictionary of all iface, and address information those are binded to
it.

```
{
  'en0': {
    'LINK': [
      { 'addr': 'ac:bc:32:8f:e5:71'}
    ],
    'INET': [
      {
        'broadcast': '172.18.5.255',
        'netmask': '255.255.255.0',
        'addr': '172.18.5.252'
      }
    ]
  }
}
```

**arguments**:

-   `iface_prefix`:
    is a string or `''` to specify what iface should be chosen.

    `net.get_host_devices(iface_prefix="eth")` returns only `eth0`, `eth1` etc.

**return**:
a dictionary of iface and its address information.


##  net.get_host_ip4

**syntax**:
`net.get_host_ip4(iface_prefix='', exclude_prefix=None)`

Get ipv4 addresses on local host.

If `iface_prefix` is specified, it returns only those whose iface name
starts with `iface_prefix`.

If `exclude_prefix` is specified, it does not return those whose iface name
starts with `exclude_prefix`.

`127.0.0.1` will not be returned.

**arguments**:

-   `iface_prefix`:
    is a string or a list of string to specify what iface should be chosen.
    By default it is `""` thus it returns ips of all iface.

    `net.get_host_ip4(iface_prefix="eth0")` returns only ipv4 addresses those
    are binded to `eth0`.

-   `exclude_prefix`:
    is a string or a list of string to specify what iface should not be
    chosen.
    By default it is `None` thus no iface is excluded.

**return**:
a list of ipv4 addresses.


##  net.ip_class

**syntax**:
`net.ip_class(ip)`

Return the class of `ip`: `net.PUB` or `net.INN`.

**return**:
`net.PUB` or `net.INN`.


##  net.ips_prefer

**syntax**:
`net.ips_prefer(ip_list, preference)`

Reorder `ip_list` according to `preference`.
-   If `preference` is `net.PUB`, it returns a new list with public ips before
    internal ips.
-   If `preference` is `net.INN`, it returns a new list with internal ips
    before public ips.

**arguments**:

-   `ip_list`:
    list of ip strings.

-   `preference`:
    is one of `net.PUB` and `net.INN`, to specify what ip should be added into
    the list returned.

**return**:
a new list of ips in `ip_list` reordered according to `preference`.


##  net.is_inn

**syntax**:
`net.is_inn(ip)`

Check if `ip` is an internal ipv4 address.

**arguments**:

-   `ip`:
    string of ipv4 address

**return**:
`True` or `False`


##  net.is_pub

**syntax**:
`net.is_pub(ip)`

Check if `ip` is a public ipv4 address.

**arguments**:

-   `ip`:
    string of ipv4 address

**return**:
`True` or `False`


##  net.is_ip4

**syntax**:
`net.is_ip4(ip)`

It checks if `ip` is a valid ipv4 string.

**arguments**:

-   `ip`:
    string or other type data.

**return**:
`True` if `ip` is valid ipv4 address. Otherwise `False`.


##  net.parse_ip_regex_str

**syntax**:
`net.parse_ip_regex_str(regexs)`

It splits a comma separated string into a list.
Each one in the result list should be a regex string.

**arguments**:

-   `regexs`:
    is a comma separated string, such as: `192[.]168[.],172[.]16[.]`.
    With this argument, it returns: `['192[.]168[.]', '172[.]16[.]']`.

    These two regex matches all ipv4 addresses those are started
    with `192.168.` or `172.16.`

**return**:
a list of regex string.


## net.ip_to_num

**syntax**:
`net.ip_to_num(ip)`

It converts the IP to 4-byte integer

**return**:
a 4-byte integer.


## net.num_to_ip

**syntax**:
`net.num_to_ip(ip_num)`

It converts the 4-byte integer to IP

**return**:
IP.


#   Commandline Tool


##  ip

**syntax**:
`python -m net ip`

It prints to stdout all ipv4 addresses, in yaml format.
See `net.get_host_ip4`.


##  devcie

**syntax**:
`python -m net device`

It prints to stdout all device, in yaml format.
See `net.get_host_devices`.


#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
