#!/bin/sh

# pip install pyflakes autopep8 autoflake isort

path="${1-.}"

fns="$(find "$path" -name "*.py" -exec echo '"{}"' \;)"

autopep8_options='--max-line-length 120'

eval pyflakes                              $fns
eval autopep8  -i $autopep8_options        $fns
eval autoflake -i                          $fns
eval isort     --force-single-line-imports $fns
