#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020, Simon Dodsley (simon@purestorage.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: purefa_network
short_description:  Manage network interfaces in a Pure Storage FlashArray
version_added: '1.0.0'
description:
    - This module manages the physical and virtual network interfaces on a Pure Storage FlashArray.
    - To manage VLAN interfaces use the I(purefa_vlan) module.
    - To manage network subnets use the I(purefa_subnet) module.
    - To remove an IP address from a non-management port use 0.0.0.0/0
author: Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
options:
  name:
    description:
      - Interface name (physical or virtual).
    required: true
    type: str
  state:
    description:
      - State of existing interface (on/off).
    required: false
    default: present
    choices: [ "present", "absent" ]
    type: str
  address:
    description:
      - IPv4 or IPv6 address of interface in CIDR notation.
      - To remove an IP address from a non-management port use 0.0.0.0/0
    required: false
    type: str
  gateway:
    description:
      - IPv4 or IPv6 address of interface gateway.
    required: false
    type: str
  mtu:
    description:
      - MTU size of the interface. Range is 1280 to 9216.
    required: false
    default: 1500
    type: int
extends_documentation_fragment:
    - purestorage.flasharray.purestorage.fa
'''

EXAMPLES = '''
- name: Configure and enable network interface ct0.eth8
  purefa_network:
    name: ct0.eth8
    gateway: 10.21.200.1
    address: "10.21.200.18/24"
    mtu: 9000
    state: present
    fa_url: 10.10.10.2
    api_token: c6033033-fe69-2515-a9e8-966bb7fe4b40

- name: Disable physical interface ct1.eth2
  purefa_network:
    name: ct1.eth2
    state: absent
    fa_url: 10.10.10.2
    api_token: c6033033-fe69-2515-a9e8-966bb7fe4b40

- name: Enable virtual network interface vir0
  purefa_network:
    name: vir0
    state: present
    fa_url: 10.10.10.2
    api_token: c6033033-fe69-2515-a9e8-966bb7fe4b40

- name: Remove an IP address from iSCSI interface ct0.eth4
  purefa_network:
    name: ct0.eth4
    address: 0.0.0.0/0
    gateway: 0.0.0.0
    fa_url: 10.10.10.2
    api_token: c6033033-fe69-2515-a9e8-966bb7fe4b40
'''

RETURN = '''
'''

try:
    from netaddr import IPAddress, IPNetwork
    HAS_NETADDR = True
except ImportError:
    HAS_NETADDR = False

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.flasharray.plugins.module_utils.purefa import get_system, purefa_argument_spec


def _get_interface(module, array):
    """Return Interface or None"""
    interface = {}
    if module.params['name'][0] == "v":
        try:
            interface = array.get_network_interface(module.params['name'])
        except Exception:
            return None
    else:
        try:
            interfaces = array.list_network_interfaces()
        except Exception:
            return None
        for ints in range(0, len(interfaces)):
            if interfaces[ints]['name'] == module.params['name']:
                interface = interfaces[ints]
                break
    return interface


def update_interface(module, array, interface):
    """Modify Interface settings"""
    changed = True
    if not module.check_mode:
        current_state = {'mtu': interface['mtu'],
                         'gateway': interface['gateway'],
                         'address': interface['address'],
                         'netmask': interface['netmask']}
        if not module.params['address']:
            address = interface['address']
        else:
            if module.params['gateway'] and module.params['gateway'] not in IPNetwork(module.params['address']):
                module.fail_json(msg='Gateway and subnet are not compatible.')
            elif not module.params['gateway'] and interface['gateway'] not in [None, IPNetwork(module.params['address'])]:
                module.fail_json(msg='Gateway and subnet are not compatible.')
            address = str(module.params['address'].split("/", 1)[0])
        if not module.params['mtu']:
            mtu = interface['mtu']
        else:
            if not 1280 <= module.params['mtu'] <= 9216:
                module.fail_json(msg='MTU {0} is out of range (1280 to 9216)'.format(module.params['mtu']))
            else:
                mtu = module.params['mtu']
        if module.params['address']:
            netmask = str(IPNetwork(module.params['address']).netmask)
        else:
            netmask = interface['netmask']
        if not module.params['gateway']:
            gateway = interface['gateway']
        else:
            cidr = str(IPAddress(netmask).netmask_bits())
            full_addr = address + "/" + cidr
            if module.params['gateway'] not in IPNetwork(full_addr):
                module.fail_json(msg='Gateway and subnet are not compatible.')
            gateway = module.params['gateway']
        new_state = {'address': address,
                     'mtu': mtu,
                     'gateway': gateway,
                     'netmask': netmask}
        if new_state == current_state:
            changed = False
        else:
            if 'management' in interface['services'] or 'app' in interface['services'] and address == "0.0.0.0/0":
                module.fail_json(msg="Removing IP address from a management or app port is not supported")
            try:
                if new_state['gateway'] is not None:
                    array.set_network_interface(interface['name'],
                                                address=new_state['address'],
                                                mtu=new_state['mtu'],
                                                netmask=new_state['netmask'],
                                                gateway=new_state['gateway'])
                else:
                    array.set_network_interface(interface['name'],
                                                address=new_state['address'],
                                                mtu=new_state['mtu'],
                                                netmask=new_state['netmask'])
            except Exception:
                module.fail_json(msg="Failed to change settings for interface {0}.".format(interface['name']))
        if not interface['enabled'] and module.params['state'] == 'present':
            try:
                array.enable_network_interface(interface['name'])
                changed = True
            except Exception:
                module.fail_json(msg="Failed to enable interface {0}.".format(interface['name']))
        if interface['enabled'] and module.params['state'] == 'absent':
            try:
                array.disable_network_interface(interface['name'])
                changed = True
            except Exception:
                module.fail_json(msg="Failed to disable interface {0}.".format(interface['name']))

    module.exit_json(changed=changed)


def main():
    argument_spec = purefa_argument_spec()
    argument_spec.update(
        dict(
            name=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            address=dict(type='str'),
            gateway=dict(type='str'),
            mtu=dict(type='int', default=1500),
        )
    )

    module = AnsibleModule(argument_spec,
                           supports_check_mode=True)

    if not HAS_NETADDR:
        module.fail_json(msg='netaddr module is required')

    array = get_system(module)
    interface = _get_interface(module, array)
    if not interface:
        module.fail_json(msg="Invalid network interface specified.")

    update_interface(module, array, interface)

    module.exit_json(changed=False)
    module.exit_json(changed=False)


if __name__ == '__main__':
    main()
