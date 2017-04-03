#!/bin/sh

# usage:
#     script/t.sh [-v]
#     script/t.sh [-v] zkutil
#     script/t.sh [-v] zkutil.test
#     script/t.sh [-v] zkutil.test_zkutil
#     script/t.sh [-v] zkutil.test_zkutil.TestZKUtil
#     script/t.sh [-v] zkutil.test_zkutil.TestZKUtil.test_lock_data

flag=
while getopts v opname; do
    case $opname in
        v)
            flag="-v"
            shift
            ;;
    esac
done

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
    PYTHONPATH="$(pwd)" python2 -m unittest discover -c $flag --failfast -s "$pkg"
else
    # it is a class or function: pykit.zkutil.test.test_zkutil.TestXXX
    PYTHONPATH="$(pwd)" python2 -m unittest -c $flag --failfast "$pkg"
fi
