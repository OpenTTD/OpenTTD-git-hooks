#!/usr/bin/env python3

import re, sys

PAT_TAB = re.compile("\t*[^\t]*$")

def checkascii(l):
  return any((ord(c) < 32 or ord(c) > 127) and c != '\t' for c in l)

status = 0
filename = None
line = None

for l in open(sys.argv[1]):
  l = l.rstrip("\n")

  if l.startswith("+++"):
    line = 1
    filename = l[4:]
    if checkascii(filename):
      sys.stderr.write("*** Filename is non-ASCII: '{}'\n".format(filename))
      status = 1
  elif l.startswith("@@"):
    line = int(l.split()[2].split(",")[0])
  elif l.startswith("+"):
    l = l[1:]
    if checkascii(l):
      sys.stderr.write("*** {}:{}: Non-ASCII found: '{}'\n".format(filename, line, l))
      status = 1
    if l != l.rstrip():
      sys.stderr.write("*** {}:{}: Trailing whitespace: '{}'\n".format(filename, line, l))
      status = 1
    if not PAT_TAB.match(l):
      sys.stderr.write("*** {}:{}: Invalid tab usage: '{}'\n".format(filename, line, l))
      status = 1
    line += 1
  elif l.startswith(" "):
    line += 1

sys.exit(status)
