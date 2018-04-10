#!/usr/bin/env python3
from microseg import iacnet
from proxmoxer import ProxmoxAPI
import os

proxmox = ProxmoxAPI('proxmox01',
                     user="{}@pam".format(os.getenv('USER')),
                     password=os.getenv('proxmoxpass'),
                     verify_ssl=False)

n = iacnet('po1', 'po3', '10.42.0.1', '10.100.0.0')

machinetypes = ('lxc', 'qemu')
machines = []

vmnodes = [x['node'] for x in proxmox.nodes.get()]
for node in vmnodes:
    for mt in machinetypes:
        pr = getattr(proxmox.nodes(node), mt)
        machines.extend(pr.get())

for m in machines:
    n.addVlanInt(int(m['vmid']), m['name'])

print ('!*********************** Cisco microseg firewall config ************')
print (n.getFWconfigs())

print ('#*********************** DNSMasq microseg config *******************')
print (n.getDnsmasqConfigs())
