#!/usr/bin/python3
from microseg import iacnet

n = iacnet('po1', 'po3', '10.100.0.0', 16, '10.42.0.1')
netlist = ( (100, 'puppet'),
            (101, 'db01'),
            (102, 'web'),
            (200, 'pdc'),
            (201, 'win10') )

for p in netlist:
    n.createVlanInt(*p)
print (n.getFWconfigs())
