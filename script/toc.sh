#!/bin/sh

doctoc --title '#   Table of Content' $(
if [ "$#" -gt 0 ]; then
    for ptn in "$@"; do
        if [ -f "$ptn" ]; then
            echo "$ptn"
        else
            find . -name "$ptn"
        fi
    done
else
    find . -name "*.md"
fi
)
