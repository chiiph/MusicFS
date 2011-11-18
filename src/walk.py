import os
import sys
import mimetypes

from ID3 import *

rootdir = sys.argv[1]

for root, folders, files in os.walk(rootdir):
  print "Walking", root
  print "Folders"
  for folder in folders:
    print folder
  print
  print "Files"
  for file in files:
    (mime, _) = mimetypes.guess_type(file)
    if mime == "audio/mpeg":
      id3 = ID3(os.path.join(root, file))
      try:
        #print file, "|"
        print id3["TRACK"]
        #print id3["TITLE"], "|", id3["ARTIST"], "|", id3["TRACK"]
      except:
        pass
  print "-"*30
