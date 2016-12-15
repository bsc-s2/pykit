#!/bin/sh

if [ $# -eq 0 ]; then
    python2 -m unittest discover -v --failfast
else
    python2 -m unittest discover -v --failfast -s "$1"
fi
