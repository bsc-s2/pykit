#!/bin/sh

# sfood -i $(find . -name "*.py" | grep -v test_) > dep-tree \
# exit 0
# cat  dep-tree \

sfood -i $(find . -name "*.py" | grep -v test_) \
| grep -v 'None, None' \
| {
    # do not track file but just module
    sed 's/\/\w\+\.\py//g'
} \
| grep -v '/test\b' \
| sort \
| uniq \
| {
    # remove self-ref
    grep -v '\((.*)\), \1'
} \
| sed 's/\bpykit\///g' \
| {
    # add dot file head
    cat <<-END
	strict digraph "dependencies" {
	    graph [
	        rankdir = "LR",
	        overlap = "scale",
	        size = "8,10",
	        ratio = "fill",
	        fontsize = "24",
	        fontname = "Helvetica",
	        clusterrank = "local"
	    ]
	    node [
	          fontsize=24
	          shape=none
	    ];
	END

    # convert tuple to dot
    # from: (('/root/.wt/lock', 'zkutil'), ('/root/.wt/lock', 'utfjson'))
    # to:   "zkutil" -> "utfjson"
    pyscript="$(cat <<-END
	import sys
	for l in sys.stdin.readlines():
	    o = eval(l)
	    print "\"{a}\"-> \"{b}\";".format(a=o[0][1], b=o[1][1])
END
)"
    python -c "$pyscript"

    # dot file end
    echo '}'
} \
| dot -Tjpg >dep-graph.jpg
