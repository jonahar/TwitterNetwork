#!/bin/bash

in=$1
out=$2
dpi=$3

if [ ! -f "$in" ] || [ -z "$out" ] ; then
    echo "Usage: svg-to-png <svg-in-file> <png-out-file> [dpi]"
    exit 1
fi

if [ -z $dpi ]; then
    dpi="50"
fi

inkscape --export-png="$out" --export-dpi=$dpi --without-gui --export-background=black "$in"
