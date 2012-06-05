#!/usr/bin/env python
import sys
from xml.parsers.expat import ExpatError

try:
    from parse import ParseConf
except ImportError:
    print "Unable to import the module parse. Is PYTHONPATH set?"
    sys.exit(1)

try:
    cluster = ParseConf('t/config.xml')
except IOError:
    print "Unable to import t/config.xml. Is the path correct?"
    sys.exit(1)
except ExpatError:
    print "Unable to parse, check xml file"
    sys.exit(2)

x = cluster.parse_clusterinfo()
print x
print
peers = cluster.parse_peerinfo()
print peers
print
vol = cluster.parse_volinfo()
print vol
print
clients = cluster.parse_clients()
print clients
