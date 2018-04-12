#!/bin/sh

# Check a series of commits
# Example:
#   check-commits HEAD^..HEAD

set -e

# --- Safety check
if [ -z "${GIT_DIR}" ]; then
	echo "Don't run this script from the command line." >&2
	echo " (if you want, you could supply GIT_DIR then run" >&2
	echo "  $0 <oldrev>..<newrev>)" >&2
	exit 1
fi

HOOKS_DIR=${HOOKS_DIR:-${GIT_DIR}/hooks}
tmp_msg_file=$(mktemp)
tmp_diff_file=$(mktemp)

finish() {
	rm -f ${tmp_msg_file} ${tmp_diff_file}
}
trap finish EXIT

hashes=$(git rev-list "$1")
for h in ${hashes}
do
	LC_ALL=C git diff ${h}^..${h} > ${tmp_diff_file}
	${HOOKS_DIR}/check-diff.py ${tmp_diff_file}
	git cat-file commit ${h} | sed '1,/^$/d' > ${tmp_msg_file}
	${HOOKS_DIR}/check-message.py ${tmp_msg_file} server
done
