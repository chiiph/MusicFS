from query import *

import fuse
import argparse
import sys
from time import time

import stat
import os
import errno

fuse.fuse_python_api = (0, 2)

class Stat(fuse.Stat):
    def __init__(self):
        self.st_mode = stat.S_IFDIR | 0755
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 1000
        self.st_gid = 1002
        self.st_size = 4096
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

def getFileStat(size):
    st = Stat()
    st.st_size = size
    st.st_mode = stat.S_IFREG | 0666
    return st

def isDir(path):
  if path == "/":
    return True

  path = path[1:]
  parts = path.split(os.sep)
  # artist/<band>/<record>/<song>
  # album/<record>/<song>
  # song/<song>
  if len(parts) < 1:
    raise Exception("Path incorrecto: %s", path)

  if parts[0] == "artist":
    if len(parts) == 1:
      # artist/
      return True
    if len(parts) == 2:
      # artist/<band>
      return True
    if len(parts) == 3:
      # artist/<band>/<record>
      return True

    return False

  if parts[0] == "album":
    if len(parts) == 1:
      # album/
      return True
    if len(parts) == 2:
      # album/<record>
      return True
    return False

  if parts[0] == "song":
    if len(parts) == 1:
      return True
    return False
  return False

class MusicFS(fuse.Fuse):
    def __init__(self, dirs, *args, **kw):
      fuse.Fuse.__init__(self, *args, **kw)
      self.q = Querier(dirs)
      self.q.serialize("ejemplo.xml")
      self.files = {}

    def getattr(self, path):
      st = Stat()
      if isDir(path):
        return st
      path = path[1:]
      parts = path.split(os.sep)
      if parts < 1:
        raise Exception("Path invalido")

      if parts[0] == "artist":
        if len(parts) == 4:
          # artist/<band>/<record>/<song>
          band = parts[1]
          record = parts[2]
          song = parts[3].replace(".mp3","")
          song_ref = self.q.sourceByAAS(band, record, song)

          if song_ref is None:
            return None

          return os.stat(str(song_ref))
        else:
          raise Exception("getattr invalido: %s", path)
      elif parts[0] == "album":
        if len(parts) == 3:
          # album/<record>/<song>
          record = parts[1]
          song = parts[2].replace(".mp3","")
          song_ref = self.q.sourceByAS(record, song)

          if song_ref is None:
            return None

          return os.stat(str(song_ref))
        else:
          raise Exception("getattr invalido: %s", path)
      elif parts[0] == "song":
        if len(parts) == 2:
          # song/<song>
          song = parts[1].replace(".mp3", "")
          song_ref = self.q.sourceByS(song)

          if song_ref is None:
            return None

          return os.stat(str(song_ref))
        else:
          raise Exception("getattr invalido: %s", path)

      return None

    def readdir(self, path, offset):
      yield fuse.Direntry(".")
      yield fuse.Direntry("..")

      if path == "/":
        yield fuse.Direntry("artist")
        yield fuse.Direntry("album")
        yield fuse.Direntry("song")
      else:
        path = path[1:]
        parts = path.split(os.sep)
        if parts < 1:
          raise Exception("Path invalido")

        if parts[0] == "artist":
          if len(parts) == 1:
            # artist/
            for a in self.q.artists():
              yield fuse.Direntry(str(a[0]))
          if len(parts) == 2:
            # artist/<band>
            band = parts[1]
            for a in self.q.albumsByArtist(band):
              yield fuse.Direntry(str(a[0]))
          if len(parts) == 3:
            # artist/<band>/<record>
            band = parts[1]
            record = parts[2]
            for s in self.q.songsByArtistAlbum(band, record):
              yield fuse.Direntry(str(s[0])+".mp3")
        elif parts[0] == "album":
          if len(parts) == 1:
            # album/
            for a in self.q.albums():
              yield fuse.Direntry(str(a[0]))
          if len(parts) == 2:
            # album/<record>
            record = parts[1]
            for s in self.q.songsByAlbum(record):
              yield fuse.Direntry(str(s[0])+".mp3")
        elif parts[0] == "song":
          if len(parts) == 1:
            # song/
            for a in self.q.songs():
              yield fuse.Direntry(str(a[0])+".mp3")
        else:
          raise Exception("Path invalido")

    def mknod(self, path, mode, dev):
      return 0

    def unlink(self, path):
      return 0

    def read(self, path, size, offset):
      path = path[1:]
      parts = path.split(os.sep)
      if parts < 1:
        raise Exception("Path invalido")

      if parts[0] == "artist":
        if len(parts) == 4:
          # artist/<band>/<record>/<song>
          self.files[path].seek(offset)
          return self.files[path].read(size)
        else:
          raise Exception("Archivo invalido: %s", path)
      elif parts[0] == "album":
        if len(parts) == 3:
          # album/<record>/<song>
          self.files[path].seek(offset)
          return self.files[path].read(size)
        else:
          raise Exception("Archivo invalido: %s", path)
      elif parts[0] == "song":
        if len(parts) == 2:
          # song/<song>
          self.files[path].seek(offset)
          return self.files[path].read(size)
      return ""

    def write(self, path, buf, offset):
      return 0

    def release(self, path, flags):
      if not path in self.files.keys():
        return 1

      self.files[path].close()
      del(self.files[path])

      return 0

    def open(self, path, flags):
      if path in self.files.keys():
        return 0

      path = path[1:]
      parts = path.split(os.sep)
      if parts < 1:
        raise Exception("Path invalido")

      if parts[0] == "artist":
        if len(parts) == 4:
          # artist/<band>/<record>/<song>
          band = parts[1]
          record = parts[2]
          song = parts[3].replace(".mp3", "")
          song_ref = self.q.sourceByAAS(band, record, song)

          if song_ref is None:
            return 1

          self.files[path] = open(str(song_ref), "r")
          return 0
        else:
          return 1
      elif parts[0] == "album":
        if len(parts) == 3:
          # album/<record>/<song>
          record = parts[1]
          song = parts[2].replace(".mp3", "")
          song_ref = self.q.sourceByAS(record, song)

          if song_ref is None:
            return 1

          self.files[path] = open(str(song_ref), "r")
          return 0
        else:
          return 1
      elif parts[0] == "song":
        if len(parts) == 2:
          # song/<song>
          song = parts[1].replace(".mp3", "")
          song_ref = self.q.sourceByS(song)

          if song_ref is None:
            return 1

          self.files[path] = open(str(song_ref), "r")
          return 0

      return 1

    def truncate(self, path, size):
      return 0

    def utime(self, path, times):
      return 0

    def mkdir(self, path, mode):
      return 0

    def rmdir(self, path):
      return 0

    def rename(self, pathfrom, pathto):
      return 0

    def fsync(self, path, isfsyncfile):
      return 0

def main():
  parser = argparse.ArgumentParser(description='')
  parser.add_argument('--dirs', action="store", type=str)
  parsed = parser.parse_args(args=sys.argv[-2:])

  del(sys.argv[-2:])

  usage="""
  musicfs
  """ + fuse.Fuse.fusage

  server = MusicFS(parsed.dirs, version="%prog " + fuse.__version__,
                   usage=usage, dash_s_do='setsingle')
  server.parse(errex=1)
  server.main()

if __name__ == '__main__':
  main()
