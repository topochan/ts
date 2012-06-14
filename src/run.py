# run a set of tests on the mount points and time them

from __future__ import with_statement
import sys
import time
from datetime import date
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

peers = conf.parsePeerInfo()
volume = conf.parseVolInfo()
clients = conf.parseClients()
volumename=volume['name']

logdir = "~/run/GlusterFS/%s"%date.today()
logfile = "run-%s"%time.time()

for client in clients:
    env.hosts.append(client['host'])
env.user = 'root'
qa_export_server='10.16.157.24'
qa_dir="/mnt/qa"

@parallel
def __deploy():
    """Prepare to execute the list of commands."""
    with settings(warn_only = True):
        if run("showmount -e %s | grep 'qa-tools'"%qa_export_server).failed:
            print "Won't mount! qa export not found. Exiting..."
        else:
            if run("mount | grep '/mnt/qa type nfs'").failed:
                if run("test -d /mnt/qa").failed:
                    run("mkdir %s 2>/dev/null"%qa_dir)
                # run("mount -t nfs %s:/qa-tools %s -overs=3"\
                #         %(qa_export_server,qa_dir))
                run("mount -t glusterfs %s:/qa-tools %s"\
                        %(qa_export_server,qa_dir))

def __mount_clients():
    local("fab -f mount.py mount")

@parallel
def trun():
    """Run the commands to time them"""
    __deploy()
    __mount_clients()
    mounts = client['mnts']
    with cd(qa_dir):
        for mount in mounts:
            run("./run.sh %s"%mount)
