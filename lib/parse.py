# Parse the cluster spec configuration

from xml.dom.minidom import parse

class ParseConf:
    """A cluster definition parser.

    Parses the given xml file and extracts the necessary volume information
    needed to create a volume and start it.
    """

    def __init__(self, ifile):
        dom = parse(ifile)
        # The root node is expected to be named as "cluster"
        self.root = dom.getElementsByTagName("cluster")[0]
        self.peers = dom.getElementsByTagName("peers")[0]
        self.volume = dom.getElementsByTagName("volume")[0]
        self.clients = dom.getElementsByTagName("clients")[0]

    def parseClusterInfo(self):
        cluster = {}
        root = self.root
        cluster['version'] = root.getAttribute("version")
        return cluster

    def parsePeerInfo(self):
        peers = []
        peerobj = self.peers
        for p in peerobj.getElementsByTagName("peer"):
            for peer in p.childNodes:
                if peer.nodeType == peer.TEXT_NODE:
                    peers.append(peer.data)
        return peers

    def parseVolInfo(self):
        volume = {}
        export = {}
        vol = self.volume
        volume['name'] = vol.getElementsByTagName('name')[0].childNodes[0].data
        volume['type'] = vol.getElementsByTagName('type')[0].childNodes[0].data
        try:
            volume['count'] = vol.getElementsByTagName('count')[0].childNodes[0]\
                .data
        except IndexError:
            volume['count'] = None
        volume['transport'] = vol.getElementsByTagName('transport')[0].\
            childNodes[0].data
        volume['exports'] = []
        for v in vol.getElementsByTagName("export"):
            export['host'] = v.getElementsByTagName("host")[0].childNodes[0].\
                data
            # Parse the list of export directories per host
            dirs = []
            for d in v.getElementsByTagName("dir"):
                for directory in d.childNodes:
                    if directory.nodeType == directory.TEXT_NODE:
                        dirs.append(directory.data)
            export['dirs'] = dirs
            volume['exports'].append(export)
            export = {}
        return volume

    def parseClients(self):
        clients = []
        clnt = self.clients
        cl = {}
        cli = []
        for client in clnt.getElementsByTagName("client"):
            cl['host'] = client.getAttribute('host')
            cl['protocol'] = client.getElementsByTagName('protocol')[0].\
                childNodes[0].data
            for c in client.getElementsByTagName("mnt"):
                for mnt in c.childNodes:
                    if mnt.nodeType == mnt.TEXT_NODE:
                        cli.append(mnt.data)
            cl['mnts'] = cli
            cli = []
            clients.append(cl)
            cl = {}
        return clients
