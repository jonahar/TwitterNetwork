#!/bin/bash
# create a release tarball
#
# usage "make-release-tar.sh <version>"
# e.g. "make-release-tar.sh 0.1"


version="$1"
if [[ -z "$version" ]] ; then
    version="0.0.0"
fi

tar_name="TwitterNetwork-v${version}.tar.gz"


tar -czvf "$tar_name" TwitterAPI/*.py TwitterMine/*.py conf/* TwitterGraph/*.py TwitterGraph/gephi_automated/* clustering/*.py
