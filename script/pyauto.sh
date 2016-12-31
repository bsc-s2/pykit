#!/bin/sh

path="${1-.}"

find "$path" -name "*.py" | while read fn; do
    pyflakes      "$fn"
    autopep8  -i  "$fn"
    autoflake -i  "$fn"
    isort         "$fn"
done
