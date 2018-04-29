#!/usr/bin/env python3

import re, sys

PAT_TAB = re.compile("#?\t*[^\t]*$")

def checkascii(l):
  return any((ord(c) < 32 or ord(c) > 127) and c != '\t' for c in l)

status = 0
filename = None
line = None
is_source = False

for l in open(sys.argv[1], encoding="utf-8"):
  l = l.rstrip("\n")

  if l.startswith("+++"):
    line = 1
    filename = l[4:].strip()
    if checkascii(filename):
      sys.stderr.write("*** Filename is non-ASCII: '{}'\n".format(filename))
      status = 1
    is_source = (filename.find("3rdparty") < 0) and filename.endswith((".cpp", ".c", ".hpp", ".h"))
  elif l.startswith("@@"):
    line = int(l.split()[2].split(",")[0])
  elif l.startswith("+"):
    l = l[1:]
    if is_source and checkascii(l):
      sys.stderr.write("*** {}:{}: Non-ASCII found: '{}'\n".format(filename, line, l))
      status = 1
    if l != l.rstrip():
      sys.stderr.write("*** {}:{}: Trailing whitespace: '{}'\n".format(filename, line, l))
      status = 1
    if is_source and not PAT_TAB.match(l):
      sys.stderr.write("*** {}:{}: Invalid tab usage: '{}'\n".format(filename, line, l))
      status = 1
    if is_source and (l.find("\t#") >= 0):
      sys.stderr.write("*** {}:{}: Preprocessor hash is put into the first column, before the tab indentation: '{}'\n".format(filename, line, l))
      status = 1
    if is_source and l.startswith("  "):
      sys.stderr.write("*** {}:{}: Use tabs for indentation: '{}'\n".format(filename, line, l))
      status = 1
    line += 1
  elif l.startswith(" "):
    line += 1
  elif l == "\\ No newline at end of file":
    sys.stderr.write("*** {}: No newline at end of file\n".format(filename))
    status = 1

sys.exit(status)
