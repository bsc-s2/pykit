#! /usr/bin/sh

echo $* | sed 's/ //g' | tr -d ["\n"] > /tmp/foo
