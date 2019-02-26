r"""Command-line tool to validate and pretty-print JSON

Usage::

    $ echo '{"json":"obj"}' | python -m pykit.p3json.tool
    {
        "json": "obj"
    }
    $ echo '{ 1.2:3.4}' | python -m pykit.p3json.tool
    Expecting property name enclosed in double quotes: line 1 column 3 (char 2)

"""
import argparse
import collections
import sys

from pykit import p3json


def main():
    prog = 'python -m pykit.p3json.tool'
    description = ('A simple command line interface for p3json module '
                   'to validate and pretty-print JSON objects.')
    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument('infile', nargs='?', type=argparse.FileType(),
                        help='a JSON file to be validated or pretty-printed')
    parser.add_argument('outfile', nargs='?', default='-',
                        help='write the output of infile to outfile')
    parser.add_argument('--sort-keys', action='store_true', default=False,
                        help='sort the output of dictionaries alphabetically by key')
    options = parser.parse_args()

    infile = options.infile or sys.stdin
    sort_keys = options.sort_keys

    with infile:
        try:
            if sort_keys:
                obj = p3json.load(infile)
            else:
                obj = p3json.load(infile,
                                  object_pairs_hook=collections.OrderedDict)
        except ValueError as e:
            raise SystemExit(e)

    if options.outfile == '-':
        outfile = sys.stdout
    else:
        outfile = open(options.outfile, 'w')

    with outfile:
        p3json.dump(obj, outfile, sort_keys=sort_keys, indent=4)
        outfile.write('\n')


if __name__ == '__main__':
    main()
