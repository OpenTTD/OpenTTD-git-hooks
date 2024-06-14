#!/usr/bin/env python3

import re, sys

# Player facing changes:
KEYWORDS = "(Add|"        # : Similar to Feature, but for small functionalities.
KEYWORDS += "Change|"     # : Changing existing behavior to such an extent as to be player visible.
KEYWORDS += "Doc|"        # : Update player-facing documentation contained in `docs/` folder or developer facing documentation in the various markdown files.
KEYWORDS += "Feature|"    # : Adding a significant new functionality to the game. This can be small in code-size, but is meant for bigger things from a player perspective.
KEYWORDS += "Fix|"        # : Fixing an issue with the game (as seen by the player).
KEYWORDS += "Remove|"     # : Completely removing a functionality.
KEYWORDS += "Revert|"     # : Reverting an earlier Feature / Add / Change / Fix / Remove.
KEYWORDS += "Update|"     # : Translation updates.

# Developer only visible changes:
KEYWORDS += "Codechange|" # : Changes to the code the player is not going to notice. refactors, modernization, etc.
KEYWORDS += "Codefix|"    # : Fixing problems in earlier commits that players won't notice: wrong comments, missing files, CI changes.
KEYWORDS += "Cleanup|"    # : Similar to Codechange, but when it is more about removing old code, rather than an actual change.
KEYWORDS += "Prepare"     #
KEYWORDS += "Upgrade)"    #

ISSUE = "#\\d+"
COMMIT = "[0-9a-f]{4,}"

MSG_PAT1 = re.compile(KEYWORDS + "$")
MSG_PAT2 = re.compile(KEYWORDS + " " + ISSUE + "$")
MSG_PAT3 = re.compile(KEYWORDS + " " + COMMIT + "$")
MSG_PAT4 = re.compile(COMMIT + "$")

ERROR = """
*** First line of message must match: '<keyword>( #<issue>| <commit>(, (<keyword> #<issue>|<commit>))*)?: ([<section])? <Details>'
Valid <keyword>: """+KEYWORDS+"""
Examples:
  'Fix: [YAPF] Infinite loop in pathfinder.'
  'Fix #5926: [YAPF] Infinite loop in pathfinder.'
  'Fix 80dffae130: Warning about unsigned unary minus.
  'Fix #6673, 99bb3a95b4: Store the map variety setting in the samegame.'
  'Revert d9065fbfbe, Fix #5922: ClientSizeChanged is only called via WndProcGdi which already has the mutex.'
  'Fix #1264, Fix #2037, Fix #2038, Fix #2110: Rewrite the autoreplace kernel.'
"""

is_client = sys.argv[2] = 'client'

first_line = True
for l in open(sys.argv[1], encoding="utf-8"):
  l = l.rstrip("\n")

  # Skip comments on client side:
  #   There are various ways how parts of the commit message can be ignored.
  #   One method is by using some comment character (# by default).
  #   Another is by using scissor lines.
  #   We cannot tell which method is active, so we make a convenient assumption.
  # On server side we always check the whole message, since there are no longer any comments.
  if is_client and l.startswith("#"):
    continue

  # Check trailing whitespace
  if l != l.rstrip():
    sys.stderr.write("*** Message contains trailing whitespace: '{}'\n".format(l))
    sys.exit(1)

  # Check ASCII, and no control chars
  if any(ord(c) < 32 or ord(c) > 127 for c in l):
    sys.stderr.write("*** Message contains non-ASCII characters or tabs: '{}'\n".format(l))
    sys.exit(1)

  # Check first line
  if first_line:
    first_line = False

    parts = l.split(": ", 1)
    if len(parts) != 2:
      sys.stderr.write(ERROR)
      sys.exit(1)

    prefixes = parts[0].split(", ")
    first_prefix = True
    for p in prefixes:
      if (len(prefixes) == 1 and MSG_PAT1.match(p)) or MSG_PAT2.match(p) or MSG_PAT3.match(p) or (not first_prefix and MSG_PAT4.match(p)):
        first_prefix = False
      else:
        sys.stderr.write(ERROR)
        sys.exit(1)
