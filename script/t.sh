#!/bin/sh

# usage:
#     script/t.sh [-v]
#     script/t.sh [-v] zkutil
#     script/t.sh [-v] zkutil.test
#     script/t.sh [-v] zkutil.test_zkutil
#     script/t.sh [-v] zkutil.test_zkutil.TestZKUtil
#     script/t.sh [-v] zkutil.test_zkutil.TestZKUtil.test_lock_data

flag=
ut_debug=
verbosity=
while [ "$#" -gt 0 ]; do

    # -v or -vv
    if [ "${1:0:2}" = "-v" ]; then
        flag='-v'
        verbosity="v$verbosity"

        # -vv
        more=${1:2}

        if [ "$more" = 'v' ]; then
            verbosity="v$verbosity"
        fi
        shift
    else
        break
    fi
done

if [ "$verbosity" = 'vv' ]; then
    ut_debug=1
fi

pkg="${1%/}"

while [ ! -d pykit ]; do
    pkg="$(basename $(pwd)).$pkg"
    cd ..
done

pkg="${pkg%.}"

# Find test from a subdir or a module.
# Add env variable PYTHONPATH to let all modules in sub folder can find the
# root package.

# UT_DEBUG controls if dd() should output debug log to stdout.
# see ututil.py

if python -c 'import '$pkg 2>/dev/null; then
    # it is a module
    PYTHONPATH="$(pwd)" UT_DEBUG=$ut_debug python2 -m unittest discover -c $flag --failfast -s "$pkg"
else
    # it is a class or function: pykit.zkutil.test.test_zkutil.TestXXX
    PYTHONPATH="$(pwd)" UT_DEBUG=$ut_debug python2 -m unittest -c $flag --failfast "$pkg"
fi
