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
check_dep=1
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
    elif [ "$1" = "-C" ]; then
        # quick mode,  do not check dependency
        check_dep=0
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

if [ "$check_dep" = "1" ]; then
    # Check if all module can be imported properly, to find uninstalled dependency
    # module.
    echo 'check if modules are importable...'
    unimportable=
    for _mod in $(find pykit -mindepth 2 -maxdepth 2 -type f -name __init__.py); do
        mod=${_mod#pykit/}
        mod=${mod%/__init__.py}
        if msg=$(python -c 'import pykit.'$mod 2>&1); then
            if [ "$verbosity" != "" ]; then
                printf "test importing $mod: OK\n"
            fi
        else
            if [ "$verbosity" != "" ]; then
                printf "test importing $mod: ERROR:\n"
                echo "$msg"
            fi
            unimportable="$unimportable\n$(printf "    %-12s" $mod): $(echo "$msg" | tail -n1)"
        fi
    done

    if [ "$unimportable" != "" ] && [ "$verbosity" = "" ]; then
        echo "!!!"
        echo "!!! There are some module can not be imported, those might impede tests:$unimportable"
        echo "!!!"
        echo "!!! run t.sh with '-v' to see more info "
        echo "!!!"
    fi
fi


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
