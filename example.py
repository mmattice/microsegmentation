#!/usr/bin/python3
from microseg import iacnet

n = iacnet('po1', 'po3', '10.42.0.1', '10.100.0.0')
netlist = ( (100, 'puppet'),
            (101, 'db01'),
            (102, 'web'),
            (103, 'pdc'),
            (104, 'win10') )

for p in netlist:
    n.addVlanInt(*p)

print ('!*********************** Cisco microseg firewall config ************')
print (n.getFWconfigs())

print ('#*********************** DNSMasq microseg config *******************')
print (n.getDnsmasqConfigs())
