#!/usr/bin/env python3
from microseg import iacnet
import os

n = iacnet('po1', 'po3', '10.42.0.1', '10.100.0.0', supernetbits=8)

f = open('/tmp/microseg-fw.conf', 'w')
f.write('!*********************** Cisco microseg firewall config ************\n')
for conf in n.getFullCiscoFWConfigs():
    f.write(conf)
    f.write('\n')
f.close()

f = open('/tmp/microseg-dnsmasq.conf', 'w')
f.write ('#*********************** DNSMasq microseg config *******************\n')
for conf in n.getFullDnsmasqConfigs():
    f.write(conf)
    f.write('\n')
f.close()
