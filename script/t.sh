#!/bin/sh

if [ $# -eq 0 ]; then
    python2 -m unittest discover -v --failfast
else
    if [ -d "$1" ]; then
        # find test from a subdir
        python2 -m unittest discover -v --failfast -s "$1"
    else
        # find test by module[.Class[.function]]
        python2 -m unittest -v --failfast "$1"
    fi
fi
