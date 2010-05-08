#!/bin/bash

set -e

DIR="/Volumes/Oyama/Streams/cineSync Test Files/movies"

function checkPath {
	ruby -r rubygems -r cinesync -e "puts CineSync::short_hash('$1')"
	python -c "import cinesync; print cinesync.short_hash('$1')"
}


IFS='
'

checkPath ../test/small.txt

for file in `ls "$DIR"`
do
	path="${DIR}/${file}"
	echo "$file"
	if [ -f "$path" ]; then
		checkPath "$path"
	fi
done
