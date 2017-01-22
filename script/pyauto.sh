#!/bin/sh

# pip install pyflakes autopep8 autoflake isort

path="${1-.}"

fns="$(find "$path" -name "*.py" -exec echo '"{}"' \;)"

eval pyflakes                              $fns
eval autopep8  -i                          $fns
eval autoflake -i                          $fns
eval isort     --force-single-line-imports $fns
