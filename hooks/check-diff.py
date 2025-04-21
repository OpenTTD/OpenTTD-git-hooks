#!/usr/bin/env python3

import re, sys

PAT_TAB = re.compile("#?\t*[^\t]*$")
PAT_BAD_COMMENT = re.compile(r"\s*//")

def checkascii(l):
  return any((ord(c) < 32 or ord(c) > 127) and c != '\t' for c in l)

status = 0
filename = None
line = None
is_source = False
lastline = None

for l in open(sys.argv[1], encoding="utf-8"):
  l = l.rstrip("\n")

  if l.startswith("+++"):
    line = 1
    lastline = None
    filename = l[4:].strip()
    if checkascii(filename):
      sys.stderr.write("*** Filename is non-ASCII: '{}'\n".format(filename))
      status = 1
    is_source = (filename.find("3rdparty") < 0) and filename.endswith((".cpp", ".c", ".hpp", ".h", ".mm"))
  elif l.startswith("@@"):
    line = int(l.split()[2].split(",")[0])
    lastline = None
  elif l.startswith("+"):
    l = l[1:]
    lastline = "+"
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
    if is_source and PAT_BAD_COMMENT.match(l):
      sys.stderr.write("*** {}:{}: Use /* */ for free standing comments: '{}'\n".format(filename, line, l))
      status = 1
    line += 1
  elif l.startswith(" "):
    line += 1
    lastline = " "
  elif l.startswith("-"):
    # do not increment line
    lastline = "-"
  elif l == "\\ No newline at end of file" and lastline != "-":
    sys.stderr.write("*** {}: No newline at end of file\n".format(filename))
    if lastline == " ": sys.stderr.write("Please fix the existing newline problem in the file.\n")
    status = 1

sys.exit(status)
