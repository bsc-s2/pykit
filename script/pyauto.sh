#!/bin/sh

# pip install pyflakes autopep8 autoflake isort

path="${1-.}"

find "$path" -name "*.py" | while read fn; do
    pyflakes                              "$fn"
    autopep8  -i                          "$fn"
    autoflake -i                          "$fn"
    isort     --force-single-line-imports "$fn"
done
