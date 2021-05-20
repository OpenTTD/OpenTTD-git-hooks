#!/bin/sh
set -ex

HOOKS_DIR=$1

# Install matchers.
echo "::add-matcher::${HOOKS_DIR}/action/check-diff-matcher.json"
echo "::add-matcher::${HOOKS_DIR}/action/check-message-matcher.json"

# Show what commits we are evaluating.
git log --oneline HEAD^..HEAD^2

# Run the checker.
HOOKS_DIR=${HOOKS_DIR}/hooks GIT_DIR=.git ${HOOKS_DIR}/hooks/check-commits.sh HEAD^..HEAD^2

# Remove matchers.
echo "::remove-matcher owner=check-diff::"
echo "::remove-matcher owner=check-message::"
