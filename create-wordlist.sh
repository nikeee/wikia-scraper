#!/usr/bin/env bash

urldecode(){
	echo -e "$(sed 's/+/ /g;s/%\(..\)/\\x\1/g;')"
}

# Concatinate all input files,
# Remove all blanks
# Convert everything to lower case
# Remove all colons
# sort
# Remove duplicates
# Decode percent encoding
cat "$@" | sed -E -e 's/[[:blank:]]+//g' | sed 's/.*/\L&/' | sed 's/://g' | sort | uniq | urldecode
