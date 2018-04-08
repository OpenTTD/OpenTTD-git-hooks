#!/bin/sh

git_good()
{
git "$@" >/dev/null 2>&1
if [ $? -ne 0 ]
then
echo "Command '$@' failed"
exit 1
fi
}

git_bad()
{
git "$@" >/dev/null 2>&1
if [ $? -eq 0 ]
then
echo "Command '$@' should have failed"
exit 1
fi
}

test_commit_good()
{
git_good commit -m "$1"
}

test_commit_bad()
{
git_bad commit -m "$1"
}

# reset all
rm -rf main main.git goodguy badguy

# setup main
git_good init main
cd main
git_good config --local core.autocrlf input
git_good config --local core.whitespace trailing-space,space-before-tab,indent-with-non-tab
echo "init" > readme
git_good add readme
test_commit_good "Add: Init"

cd ..
mv main/.git main.git
rm -rf main
git_good --git-dir=main.git config core.bare true

cd main.git/hooks
ln -s -t . ../../../hooks/*
cd ../..

# setup goodguy
echo "goodguy"
git_good clone main.git goodguy
cd goodguy
git_good config --local core.autocrlf input
git_good config --local core.whitespace trailing-space,space-before-tab,indent-with-non-tab
cd .git/hooks
ln -s -t . ../../../../hooks/*
cd ../../../

# test cases
cp cases/* goodguy
cd goodguy

git_good add case1.cpp
test_commit_bad "Add No ref"
test_commit_bad "-Add: No ref"
test_commit_bad " Add: No ref"
test_commit_bad "Add : No ref"
test_commit_bad "Add:No ref"
test_commit_good "Add: No ref"

cp case1.cpp case11.cpp
git_good add case11.cpp
test_commit_bad "Add [FS#123]: Issue ref"
test_commit_bad "Add [#123]: Issue ref"
test_commit_bad "Add, #123: Issue ref"
test_commit_bad "Add  #123: Issue ref"
test_commit_bad "Add #123 : Issue ref"
test_commit_bad "Add # 123: Issue ref"
test_commit_bad "Add #123:Issue ref"
test_commit_good "Add #123: Issue ref"

cp case1.cpp case12.cpp
git_good add case12.cpp
test_commit_bad "Fix, abcdef: Commit ref"
test_commit_bad "Fix  abcdef: Commit ref"
test_commit_bad "Fix abcdef : Commit ref"
test_commit_bad "Fix abcdef:Commit ref"
test_commit_good "Fix abcdef: Commit ref"

cp case1.cpp case13.cpp
git_good add case13.cpp
test_commit_bad "Fix #123 #456: Two issue ref"
test_commit_bad "Fix #123, #456: Two issue ref"
test_commit_bad "Fix #123,Fix #456: Two issue ref"
test_commit_good "Fix #123, Fix #456: Two issue ref"

cp case1.cpp case14.cpp
git_good add case14.cpp
test_commit_bad "abcdef, Fix #456: Commit and issue ref"
test_commit_bad "Fix abcdef #456: Commit and issue ref"
test_commit_bad "Fix abcdef, #456: Commit and issue ref"
test_commit_good "Fix abcdef, Fix #456: Commit and issue ref"

cp case1.cpp case15.cpp
git_good add case15.cpp
test_commit_bad "#123, Fix abcdef: Issue and commit ref"
test_commit_bad "Fix #123 abcdef: Issue and commit ref"
test_commit_bad "Fix #123,abcdef: Issue and commit ref"
test_commit_good "Fix #123, abcdef: Issue and commit ref"

cp case1.cpp case16.cpp
git_good add case16.cpp
test_commit_good "Fix #123, Fix abcdef: Issue and commit ref"

cp case1.cpp case17.cpp
git_good add case17.cpp
test_commit_bad "fedcba, Fix abcdef: Two commit ref"
test_commit_bad "Fix fedcba abcdef: Two commit ref"
test_commit_good "Fix fedcba, abcdef: Two commit ref"

cp case1.cpp case18.cpp
git_good add case18.cpp
test_commit_good "Fix fedcba, Fix abcdef: Two commit ref"

git_good add case2.cpp
test_commit_bad "Add: Whitespace"
git_good reset case2.cpp

git_good add case3.cpp
test_commit_bad "Add: Tabs"
git_good reset case3.cpp

git_good add case4.cpp
test_commit_bad "Add: Mixed indent"
git_good reset case4.cpp

# various cases in 3rdparty and non-c++ sources
#git_good add case5.cpp
#test_commit_bad "Add: Space indent"
#git_good reset case5.cpp

git_good push

# setup badguy
cd ..
echo "badguy"
git_good clone main.git badguy
cd badguy

cp case1.cpp case19.cpp
git_good add case19.cpp
test_commit_good "fixit"
git_bad push

cp ../cases/case2.cpp .
git_good add case2.cpp
git_good commit --amend -m "Fix: Message"
git_bad push

cd ..
