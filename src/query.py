import os
import mimetypes

from rdflib import Graph
from rdflib import URIRef, Literal, BNode
from rdflib import Namespace, RDF

from ID3 import *

class Querier(object):
  def __init__(self, paths):
    object.__init__(self)

    self.paths = paths.split(":")
    self.graph = Graph()

    self.graph.bind("dc", "http://purl.org/dc/elements/1.1/")
    self.graph.bind("foaf", "http://xmlns.com/foaf/0.1/")
    self.graph.bind("mo", "http://purl.org/ontology/mo/")

    self.FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    self.MO = Namespace("http://purl.org/ontology/mo/")
    self.DC = Namespace("http://purl.org/dc/elements/1.1/")

    self.initNs = dict(foaf=self.FOAF,
                       mo=self.MO,
                       dc=self.DC)

    self.bands = {}
    self.records = {}
    for p in self.paths:
      self.processPath(p)

  def processPath(self, path):
    for root, folders, files in os.walk(os.path.abspath(path)):
      for file in files:
        (mime, _) = mimetypes.guess_type(file)
        if mime is None:
          continue
        t = mimetypes.guess_extension(mime)
        if not t is None and t == ".mp3":
          id3 = ID3(os.path.join(root, file))

          title = id3.get("TITLE")
          if title is None:
            title = file

          track_number = id3.get("TRACKNUMBER")
          if track_number is None:
            track_number = "0"

          album = id3.get("ALBUM")
          if album is None:
            album = "Unknown album"

          artist = id3.get("ARTIST")
          if artist is None:
            artist = "Unknown artist"

          band = None
          if not artist in self.bands.keys():
            band = BNode()

            self.graph.add((band, RDF.type, self.MO["MusicGroup"]))
            self.graph.add((band, self.FOAF["name"], Literal(artist)))
            self.bands[artist] = band
          else:
            band = self.bands[artist]

          record = None
          if not album in self.records.keys():
            record = BNode()
            self.graph.add((record, self.DC["title"], Literal(album)))
            self.graph.add((band, self.MO["Record"], record))
            self.records[album] = record
          else:
            record = self.records[album]

          track = BNode()

          self.graph.add((track, self.DC["title"], Literal(title)))
          self.graph.add((track, self.MO["track_number"], track_number))
          self.graph.add((track, self.DC["source"], Literal(os.path.join(root, file))))

          self.graph.add((record, self.MO["track"], track))

  def serialize(self, path):
    self.graph.serialize(path, format="pretty-xml", max_depth=3)

  def artists(self):
    return self.graph.query('SELECT ?band WHERE '
                            '{ ?b a mo:MusicGroup . ?b foaf:name ?band }',
                            initNs=self.initNs)

  def hasArtist(self, artist):
    return len(self.graph.query('SELECT ?b WHERE '
                                '{ ?b a mo:MusicGroup . ?b foaf:name "'+artist+'" }',
                                initNs=self.initNs)) > 0

  def albums(self):
    return self.graph.query('SELECT ?record ?band WHERE { ?b a mo:MusicGroup . ?b foaf:name ?band . '
                            '?b mo:Record ?c . ?c dc:title ?record }',
                            initNs=self.initNs)

  def hasAlbum(self, artist, album):
    return len(self.graph.query('SELECT ?c WHERE { ?b a mo:MusicGroup . '
                                '?b foaf:name "'+artist+'" . '
                                '?b mo:Record ?c . ?c dc:title "'+album+'" }',
                                initNs=self.initNs)) > 0

  def songs(self):
    return self.graph.query('SELECT ?track WHERE {'
                            ' ?b a mo:MusicGroup .'
                            ' ?b mo:Record ?c .'
                            ' ?c mo:track ?t .'
                            ' ?t dc:title ?track }',
                            initNs=self.initNs)

  def hasSong(self, artist, album, song):
    return len(self.graph.query('SELECT ?t WHERE { ?b a mo:MusicGroup .'
                                ' ?b foaf:name "'+artist+'" . ?b mo:Record ?c .'
                                ' ?c dc:title "'+album+'" . ?c mo:track ?t .'
                                ' ?t dc:title "'+song+'" }',
                                initNs=self.initNs)) > 0

  def albumsByArtist(self, artist):
    return self.graph.query('SELECT ?record WHERE { ?b a mo:MusicGroup . '
                            '?b foaf:name "'+artist+'" . '
                            '?b mo:Record ?c . ?c dc:title ?record }',
                            initNs=self.initNs)

  def songsByArtistAlbum(self, artist, album):
    return self.graph.query('SELECT ?track WHERE { ?b a mo:MusicGroup .'
                            ' ?b foaf:name "'+artist+'" . ?b mo:Record ?c .'
                            ' ?c dc:title "'+album+'" . ?c mo:track ?t .'
                            ' ?t dc:title ?track }',
                            initNs=self.initNs)

  def songsByAlbum(self, album):
    return self.graph.query('SELECT ?track WHERE { ?b a mo:MusicGroup .'
                            ' ?b mo:Record ?c .'
                            ' ?c dc:title "'+album+'" . ?c mo:track ?t .'
                            ' ?t dc:title ?track }',
                            initNs=self.initNs)

  def sourceByAAS(self, artist, album, song):
    for a in self.graph.query('SELECT ?source  WHERE { ?b a mo:MusicGroup .'
                              ' ?b foaf:name "'+artist+'" . ?b mo:Record ?c .'
                              ' ?c dc:title "'+album+'" . ?c mo:track ?t .'
                              ' ?t dc:title "'+song+'" . ?t dc:source ?source }',
                              initNs=self.initNs):
      return a[0]
    return None


  def sourceByAS(self, album, song):
    for a in self.graph.query('SELECT ?source  WHERE { ?b a mo:MusicGroup .'
                              ' ?b mo:Record ?c .'
                              ' ?c dc:title "'+album+'" . ?c mo:track ?t .'
                              ' ?t dc:title "'+song+'" . ?t dc:source ?source }',
                              initNs=self.initNs):
      return a[0]
    return None

  def sourceByS(self, song):
    for a in self.graph.query('SELECT ?source  WHERE { ?b a mo:MusicGroup .'
                              ' ?b mo:Record ?c .'
                              ' ?c mo:track ?t .'
                              ' ?t dc:title "'+song+'" . ?t dc:source ?source }',
                              initNs=self.initNs):
      return a[0]
    return None

  def sourceExists(self, source):
    return len(self.graph.query('SELECT ?source  WHERE { ?b a mo:MusicGroup .'
                                ' ?b mo:Record ?c .'
                                ' ?c mo:track ?t .'
                                ' ?t dc:source ?source }',
                                initNs=self.initNs)) > 0
