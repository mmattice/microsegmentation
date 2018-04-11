#!/usr/bin/python3

from socket import inet_ntoa, inet_aton
from struct import pack, unpack
import attr

def calcDottedNetmask(mask):
    bits = 0xffffffff ^ (1 << 32 - mask) - 1
    return inet_ntoa(pack('>I', bits))

def addr2int(addr):
    return unpack('>I', inet_aton(addr))[0]

def int2addr(i):
    return inet_ntoa(pack('>I', i))

@attr.s
class network(object):
    vlan = attr.ib()
    desc = attr.ib()
    netaddr = attr.ib()
    netmask = attr.ib()

    def _getnet_(self):
        inetaddr = addr2int(self.netaddr)
        fwip = int2addr(inetaddr + 1)
        sbip = int2addr(inetaddr + 2)
        ip = int2addr(inetaddr + 3)
        mask = calcDottedNetmask(self.netmask)
        return { 'ip' : ip,
                 'fwip' : fwip,
                 'sbip' : sbip,
                 'mask' : mask,
                 'desc' : self.desc,
                 'vlan' : self.vlan,
                 'network' : self.netaddr,
        }

    def getCiscoFWConfig(self, intname, dhcpserver):
        fargs = self._getnet_()
        ints = []
        ints.append('interface {}.{}'.format(intname,fargs['vlan']))
        ints.append('  ! network address {network}/{mask}'.format(**fargs))
        ints.append('  vlan {vlan}'.format(**fargs))
        ints.append('  description {desc}'.format(**fargs))
        ints.append('  nameif {desc}'.format(**fargs))
        ints.append('  dhcprelay server {}'.format(dhcpserver))
        ints.append('  ip address {fwip} {mask} standby {sbip}'.format(**fargs))
        ints.append('  exit')
        ints.append('dhcprelay enable {desc}'.format(**fargs))
        ints.append('')
        return ints

    def getDnsmasqConfig(self, leasetime='1h'):
        confs = []
        fargs = self._getnet_()
        fargs['leasetime'] = leasetime
        confs.append('dhcp-range=vlan{vlan},{ip},{ip},{mask},{leasetime}'.format(**fargs))
        confs.append('dhcp-option=vlan{vlan},option:router,{fwip}'.format(**fargs))
        return confs


@attr.s
class iacnet(object):
    fwint = attr.ib()
    swint = attr.ib()
    dhcpserver = attr.ib()
    basenet = attr.ib()
    supernetbits = attr.ib(default=11)  # gives a /21 -- 256 8 IP networks
    basevlan = attr.ib(default=100) # proxmox starting ID
    netbits = attr.ib(default=3)    # 2^3=8 ips per network
    nets = []

    def createVlanInt(self, vlan, name):
        ibasenet = addr2int(self.basenet)
        inetaddr = ibasenet + (vlan - self.basevlan) * (2 ** self.netbits)
        n = network(vlan, name, int2addr(inetaddr), 32 - self.netbits)
        return n

    def addVlanInt(self, vlan, name):
        n = self.createVlanInt(vlan, name)
        self.nets.append(n)

    def getFWconfigs(self):
        sl = []
        for n in self.nets:
            sl.extend(n.getCiscoFWConfig(self.fwint, self.dhcpserver))
        return '\n'.join(sl)

    def getDnsmasqConfigs(self):
        sl = []
        for n in self.nets:
            sl.extend(n.getDnsmasqConfig())
        return '\n'.join(sl)

    def getFullCiscoFWConfigs(self):
        count = 2**(self.supernetbits - self.netbits)
        i = 0
        while i < count:
            vlan = self.basevlan + i
            n = self.createVlanInt(vlan, 'vlan{}'.format(vlan))
            yield '\n'.join(n.getCiscoFWConfig(self.fwint, self.dhcpserver))
            i += 1

    def getFullDnsmasqConfigs(self, leasetime='1h'):
        count = 2**(self.supernetbits - self.netbits)
        i = 0
        while i < count:
            n = self.createVlanInt(self.basevlan + i, '')
            yield '\n'.join(n.getDnsmasqConfig(leasetime))
            i += 1
