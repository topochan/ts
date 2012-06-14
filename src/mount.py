#!/usr/bin/env python
# Mount the clients on the mount points listed in the conf
# if the mount points do not exist create them

from __future__ import with_statement
import sys
from fabric.api import *
from xml.parsers.expat import ExpatError
# We do not depend on PYTHONPATH for now
sys.path.extend(["../lib", "../conf"])

try:
    from parse import ParseConf
    from settings import *
except ImportError:
    print "Unable to import one of the modules. Is PYTHONPATH set?"
    sys.exit(1)

configfile = CONF

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

clients = conf.parseClients()
peers = conf.parsePeerInfo()
volume = conf.parseVolInfo()

volumename=volume['name']
# From where to mount the cluster?
# DEFAULT: picks the first peer.
server = peers[0]

env.user = 'root'

for client in clients:
    env.hosts.append(client['host'])

def mount(server=server,options=""):
    for client in clients:
        host = client['host']
        # Process the list meant only for this client
        if env.host == host:
            protocol = client['protocol']
            if protocol == "fuse":
                protocol = "glusterfs"
            else:
                options += " -overs=3" # Currently only nfsv3 is supported
            mounts = client['mnts']
            for mount in mounts:
                with settings(warn_only = True):
                    # Create the mountpoint if it does not exist
                    if run("test -d %s" % mount).failed:
                        run("mkdir -p %s" %mount)
                    # FIXME: Directory exists, but is it already mounted?
                    if run("mount -t %s %s:%s %s %s; :"%\
                               (protocol,server,volumename,mount,options)).\
                               failed:
                        print "FATAL: mounting %s on %s failed."%\
                            (volumename,mount)
                        sys.exit(1)

@parallel
def umount(mountpt=None):
    with settings(warn_only = True):
        if mountpt is not None or mountpt == "":
            if run("umount -l %s; :"%(mountpt)).failed:
                print "umount failed on %s"%host
        else:
            for client in clients:
                mounts = client['mnts']
                host = client['host']
                for mount in mounts:
                    if env.host == host:
                        if run("umount -l %s; :"%(mount)).failed:
                            print "umount failed on %s"%host

def list():
    run("mount")
