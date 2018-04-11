#!/usr/bin/env python3
from microseg import iacnet
from proxmoxer import ProxmoxAPI
import os
import sys

try:
    proxmox = ProxmoxAPI(os.environ.get('proxmoxhost','proxmox01'),
                         user="{}@pam".format(os.getenv('USER')),
                         password=os.getenv('proxmoxpass'),
                         verify_ssl=False)
except Exception as E:
    print(sys.exc_info())
    sys.exit(-1)

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

c = []
for x in n.nets:
    net = x._getnet_()
    c.append('access-list {desc}_egress extended permit icmp interface {desc} interface {desc}'.format(**net))
    c.append('access-list {desc}_ingress extended permit icmp interface {desc} interface {desc}'.format(**net))
    c.append('access-group {desc}_egress in interface {desc}'.format(**net))
    c.append('access-group {desc}_ingress out interface {desc}'.format(**net))
    c.append('')

print('\n'.join(c))

print ('\n#*********************** DNSMasq microseg config *******************')
print (n.getDnsmasqConfigs())
