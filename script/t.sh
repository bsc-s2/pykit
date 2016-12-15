#!/bin/sh

if [ $# -eq 0 ]; then
    python2 -m unittest discover -v
else
    python2 -m unittest discover -v -s "$1"
fi
