import rdflib

from rdflib import Graph
from rdflib import URIRef, Literal, BNode
from rdflib import Namespace, RDF

graph = Graph()

graph.bind("dc", "http://http://purl.org/dc/elements/1.1/")
graph.bind("foaf", "http://xmlns.com/foaf/0.1/")
graph.bind("mo", "http://purl.org/ontology/mo/")

FOAF = Namespace("http://xmlns.com/foaf/0.1/")
MO = Namespace("http://purl.org/ontology/mo/")
DC = Namespace("http://http://purl.org/dc/elements/1.1/")

band = BNode()

graph.add((band, RDF.type, MO["MusicGroup"]))
graph.add((band, FOAF["name"], Literal("U2")))

record = BNode()

# Track 01
track = BNode()

graph.add((track, DC["title"], Literal("Track 1")))
graph.add((track, MO["track_number"], "1"))
graph.add((track, DC["source"], Literal("/path/al/mp3blabla")))

graph.add((record, DC["title"], Literal("All")))
graph.add((record, MO["track"], track))

# Track 02
track = BNode()

graph.add((track, DC["title"], Literal("Track 2")))
graph.add((track, MO["track_number"], "2"))
graph.add((track, DC["source"], Literal("/path/al/mp3")))

graph.add((record, MO["track"], track))

graph.add((band, MO["Record"], record))

#graph.serialize("test.rdf", format="pretty-xml", max_depth=3)

print "Bandas"
for row in graph.query('SELECT ?band WHERE '
                       '{ ?b a mo:MusicGroup . ?b foaf:name ?band }',
                       initNs=dict(foaf=FOAF, mo=MO)):
  print row[0]

print "Discos por banda"
for row in graph.query('SELECT ?record WHERE '
                       '{ ?b a mo:MusicGroup . ?b foaf:name "U2" . '
                       '?b mo:Record ?c . ?c dc:title ?record }',
                       initNs=dict(foaf=FOAF, mo=MO, dc=DC)):
  print "U2", row[0]

print "Discos"
for row in graph.query('SELECT ?record ?band WHERE { ?b a mo:MusicGroup . ?b foaf:name ?band . '
                       '?b mo:Record ?c . ?c dc:title ?record }',
                       initNs=dict(foaf=FOAF, mo=MO, dc=DC)):
  print "AAAU2", row[0]

print "Tracks"
for row in graph.query('SELECT ?band ?record ?track ?source  WHERE { ?b a mo:MusicGroup . ?b foaf:name ?band . ?b mo:Record ?c .'
                       ' ?c dc:title ?record . ?c mo:track ?t .'
                       ' ?t dc:title ?track . ?t dc:source ?source }',
                       initNs=dict(foaf=FOAF, mo=MO, dc=DC)):
  print row


# artist/
# SELECT ?artist WHERE { ?b a mo:MusicGroup . ?b foaf:name ?artist }

# artist/<name>/
# SELECT ?record WHERE { ?b a mo:MusicGroup . ?b foaf:name "<name>" . ?b mo:Record ?c . ?c dc:title ?record }

# artist/<name>/<record>
# SELECT ?track_number ?track WHERE { ?b a mo:MusicGroup . ?b foaf:name "<name>" . ?b mo:Record ?c .
#                                     ?c dc:title "<record>" . ?c mo:track ?t .
#                                     ?t dc:title ?track . ?t mo:track_number ?track_number }

# artist/<name>/<record>/<song>
# SELECT ?source  WHERE { ?b a mo:MusicGroup . ?b foaf:name "<name>" . ?b mo:Record ?c .
#                         ?c dc:title "<record>" . ?c mo:track ?t .
#                         ?t dc:title "<song>" . ?t dc:source ?source }

# album/
# SELECT ?record ?band WHERE { ?b a mo:MusicGroup . ?b foaf:name ?band . ?b mo:Record ?c .
#                              ?c dc:title ?record }

# album/<record>/
# SELECT ?band ?track_number ?track WHERE { ?b a mo:MusicGroup . ?b foaf:name ?band . ?b mo:Record ?c .
#                                           ?c dc:title "<record>" . ?c mo:track ?t .
#                                           ?t dc:title ?track . ?t mo:track_number ?track_number }

# album/<record>/<song>
# SELECT ?band ?source ?track WHERE { ?b a mo:MusicGroup . ?b foaf:name ?band . ?b mo:Record ?c .
#                                     ?c dc:title "<record>" . ?c mo:track ?t .
#                                     ?t dc:title "<song>" . ?t dc:source ?source }

# songs/
# SELECT ?band ?track_number ?track ?record WHERE { ?b a mo:MusicGroup . ?b foaf:name ?band . ?b mo:Record ?c .
#                                                   ?c dc:title ?record . ?c mo:track ?t .
#                                                   ?t dc:title ?track . ?t mo:track_number ?track_number }
