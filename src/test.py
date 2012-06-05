# Build GlusterFS on a list of given servers
# This script is never run directly

from fabric.api import *
from settings import *

env.hosts = ['10.16.157.75']
env.user = 'root'

def build():
    print env.hosts
    run('ls')
