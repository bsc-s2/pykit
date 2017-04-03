#!/bin/sh

# usage:
#     script/t.sh
#     script/t.sh zkutil
#     script/t.sh zkutil.test
#     script/t.sh zkutil.test_zkutil
#     script/t.sh zkutil.test_zkutil.TestZKUtil
#     script/t.sh zkutil.test_zkutil.TestZKUtil.test_lock_data

pkg="${1%/}"

while [ ! -d pykit ]; do
    pkg="$(basename $(pwd)).$pkg"
    cd ..
done

pkg="${pkg%.}"

# Find test from a subdir or a module.
# Add env variable PYTHONPATH to let all modules in sub folder can find the
# root package.

if python -c 'import '$pkg 2>/dev/null; then
    # it is a module
    PYTHONPATH="$(pwd)" python2 -m unittest discover -c -v --failfast -s "$pkg"
else
    # it is a class or function: pykit.zkutil.test.test_zkutil.TestXXX
    PYTHONPATH="$(pwd)" python2 -m unittest -c -v --failfast "$pkg"
fi
