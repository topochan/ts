# Build GlusterFS on a list of given servers
from __future__ import with_statement
import sys
from fabric.api import *
from xml.parsers.expat import ExpatError
# We do not depend on PYTHONPATH for now
sys.path.extend(["../lib", "../conf"])

try:
    from parse import ParseConf
    from Build import Build
    from settings import *
except ImportError:
    print "Unable to import one of the modules. Is PYTHONPATH set?"
    sys.exit(1)

configfile = CONF
baseurl = DOWNLOADURL
src = SRC
pkg = PKG
tmp = TMP
installbase = INSTALLBASE

try:
    conf = ParseConf(configfile)
except IOError as detail:
    print "Unable to read %s. Is the path correct?"%configfile
    print detail
    sys.exit(1)
except ExpatError as detail:
    print "Unable to parse %s."%configfile
    print detail
    sys.exit(2)

cluster = conf.parseClusterInfo()
peers = conf.parsePeerInfo()
volume = conf.parseVolInfo()
clients = conf.parseClients()

tarball = "glusterfs-%s.tar.gz"% cluster['version']
durl = "%s/%s"%(baseurl, tarball)
volumename=volume['name']

env.hosts = peers
env.user = 'root'

build = Build(peers, cluster)

@parallel
def buildtest():
    build.buildGlusterFS(src)
