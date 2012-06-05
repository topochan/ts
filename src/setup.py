#!/usr/bin/env python
# Create a gluster setup by parsing the given configuration file
# This program is run as `fab -f setup.py function_name'

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

env.hosts = list(peers)
env.user = 'root'

# If the protocol is `fuse' build GlusterFS on clients as well
# GlusterFS is only `built', for other volume and peer operations decorators
# are used to limit the execution.
for client in clients:
    if client['protocol'].lower().replace(' ', '') == "fuse":
        env.hosts.append(client['host'])

# Remove duplicate entries from the list
env.hosts = list(set(env.hosts))

def __install():
    # Extract, configure and install
    with settings(warn_only = True):
        if run("test -d %s"% tmp).failed:
            run("mkdir -p %s"% tmp)
        with cd(src):
            if run("tar zxvf %s -C %s"% (tarball, tmp)).failed:
                print "Unable to untar, exiting..."
                sys.exit(1)
        builddir = "%s/glusterfs-%s"% (tmp, cluster['version'])
        with cd(builddir):
            if run("./configure --prefix=%s/%s"% \
                       (installbase, cluster['version'])).failed:
                print "Configuring GlusterFS installation failed, exiting..."
                sys.exit(1)
            if run("make install clean").failed:
                print "Compilation and installation of GlusterFS failed, \
exiting..."
    # Clean up the build directory
    cleanup()

# Volume creation need not happen on all the nodes do it on first
@hosts(peers[0])
def create_volume():
    volstring = "%s/%s/sbin/gluster volume create"%\
        (installbase,cluster['version'])
    count = volume['count']
    volname = volume['name']
    transport = volume['transport']
    # For a volume type replicated distribute just mention the count
    voltype = volume['type']
    if count is None or count == 0 or count == 1:
        volstring = "%s %s "%(volstring,volname)
    else:
        volstring = "%s %s replica %s transport %s "%\
            (volstring,volname,count,transport)
    # Create the export list
    exports = volume['exports']
    for export in exports:
        host = export['host']
        dirs = export['dirs']
        for direc in dirs:
            volstring = "%s %s:%s"%(volstring,host,direc)
    volstring = "%s --mode=script"%volstring
    run("%s"%volstring)

@hosts(peers[0])
def start_volume(volumename=volumename):
    run("%s/%s/sbin/gluster volume start %s --mode=script"%\
            (installbase,cluster['version'],volumename))

@hosts(peers[0])
def stop_volume(volumename=volumename):
    run("%s/%s/sbin/gluster volume stop %s --mode=script"%\
            (installbase,cluster['version'],volumename))

@hosts(peers[0])
def list_volumes(volumename=None):
    if volumename == None:
        run("%s/%s/sbin/gluster volume info"% (installbase,cluster['version']))
    else:
        run("%s/%s/sbin/gluster volume info %s"%\
                 (installbase,cluster['version'],volumename))

@hosts(peers[0])
def delete_volume(volumename=volumename):
    run("%s/%s/sbin/gluster volume delete %s --mode=script"%
            (installbase,cluster['version'],volumename))

@parallel
def start_glusterd():
    # Start gluster daemon on all the servers
    with settings(warn_only = True):
        if run("pgrep glusterd").failed:
            if run("%s/%s/sbin/glusterd"%(installbase, cluster['version']))\
                    .failed:
                print "Unable to start glusterd, exiting..."
                sys.exit(1)
        else:
            print "glusterd is already running"


@hosts(peers[0])
def peer_probe():
    for peer in peers:
        if run("%s/%s/sbin/gluster peer probe %s"%\
                   (installbase, cluster['version'],peer)).failed:
            print "Unable to peer probe, exiting..."
            sys.exit(1)

@parallel
def deploy():
    with settings(warn_only = True):
        if run("test -d %s" % src).failed:
            run("mkdir -p %s" %src)
        with cd(src):
            if run("test -f %s"% tarball).failed:
                run("wget -c %s"% durl)
            else:
                print "Source exists. Not downloading, continuing with \
installation..."
    __install()

@parallel
def cleanup():
    run("rm -rvf %s/*"% tmp)
    # run("rm -rvf /usr/src/GlusterFS")
