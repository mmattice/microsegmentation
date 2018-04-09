#!/usr/bin/python3

from socket import inet_ntoa, inet_aton
from struct import pack, unpack
import math

def calcDottedNetmask(mask):
    bits = 0xffffffff ^ (1 << 32 - mask) - 1
    return inet_ntoa(pack('>I', bits))

def addr2int(addr):
    return unpack('>I', inet_aton(addr))[0]

def int2addr(i):
    return inet_ntoa(pack('>I', i))

class iacnet(object):
    def __init__(self, fwint, swint, basenet, netclass, dhcpserver, basevlan=100, netsize=8):
        self.fwint = fwint
        self.swint = swint
        self.basenet = basenet
        self.netclass = netclass
        self.basevlan = basevlan
        self.dhcpserver = dhcpserver
        assert math.trunc(math.log2(netsize)) == math.log2(netsize)
        self.netbits = math.trunc(math.log2(netsize))

        self.ciscofw = []
        self.ciscoswitch = []

    def createVlanInt(self, vlan, name):
        ints= []
        ibasenet = addr2int(self.basenet)
        inetaddr = ibasenet + (vlan - self.basevlan) * self.netbits ** 2
        ip = int2addr(inetaddr + 1)
        sbip = int2addr(inetaddr + 2)
        mask = calcDottedNetmask(32 - self.netbits)
        ints.append('interface {}.{}'.format(self.fwint,vlan))
        ints.append('  vlan {}'.format(vlan))
        ints.append('  description {}'.format(name))
        ints.append('  nameif {}'.format(name))
        ints.append('  dhcprelay server {}'.format(self.dhcpserver))
        ints.append('  ip address {} {} standby {}'.format(ip, mask, sbip))
        ints.append('  exit')
        self.ciscofw.extend(ints)

    def getFWconfigs(self):
        return '\n'.join(self.ciscofw)

