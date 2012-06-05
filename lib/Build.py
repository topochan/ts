# Build GlusterFS on a list of given servers
from __future__ import with_statement
from fabric.api import *

class Build:
    def __init__(self, peers, cluster, volume, clients):
        self.servers = servers
        self.cluster = cluster
        self.volume = volume
        self.client = client
        self.tarball = "glusterfs-%s.tar.gz"% cluster['version']

    def buildGlusterFS(self, src):
        with settings(warn_only = True):
            if run("test -d %s" % src).failed:
                run("mkdir -p %s" %src)
            with cd(src):
                if run("test -f %s"% tarball).failed:
                    run("wget -c %s"% durl)
                else:
                    print "Source exists. Not downloading, continuing with \
installation..."

    def __install(self):
