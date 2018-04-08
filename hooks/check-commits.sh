#!/bin/sh

# Check a series of commits
# Example:
#   check-commits HEAD^..HEAD

# --- Safety check
if [ -z "$GIT_DIR" ]; then
	echo "Don't run this script from the command line." >&2
	echo " (if you want, you could supply GIT_DIR then run" >&2
	echo "  $0 <ref> <oldrev> <newrev>)" >&2
	exit 1
fi

tmp_msg="/tmp/githook_update_msg.tmp"

hashes=$(git rev-list "$1")
for h in ${hashes}
do
	git diff --check ${h}^..${h} || exit 1
	git cat-file commit ${h} | sed '1,/^$/d' > ${tmp_msg}
	${GIT_DIR}/hooks/commit-msg ${tmp_msg} || exit 1
done
