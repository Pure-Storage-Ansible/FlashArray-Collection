#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020, Simon Dodsley (simon@purestorage.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: purefa_inventory
short_description: Collect information from Pure Storage FlashArray
version_added: '1.0.0'
description:
  - Collect hardware inventory information from a Pure Storage Flasharray
author:
  - Pure Storage ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
extends_documentation_fragment:
  - purestorage.flasharray.purestorage.fa
'''

EXAMPLES = r'''
- name: collect FlashArray invenroty
  purefa_inventory:
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
- name: show inventory information
  debug:
    msg: "{{ array_info['purefa_info'] }}"

'''

RETURN = r'''
purefa_inventory:
  description: Returns the inventory information for the FlashArray
  returned: always
  type: complex
  sample: {
        "controllers": {
            "CT0": {
                "model": null,
                "serial": null,
                "status": "ok"
            },
            "CT1": {
                "model": "FA-405",
                "serial": "FHVBT52",
                "status": "ok"
            }
        },
        "drives": {
            "SH0.BAY0": {
                "capacity": 2147483648,
                "protocol": "SAS",
                "serial": "S18NNEAFA01416",
                "status": "healthy",
                "type": "NVRAM"
            },
            "SH0.BAY1": {
                "capacity": 511587647488,
                "protocol": "SAS",
                "serial": "S0WZNEACC00517",
                "status": "healthy",
                "type": "SSD"
            },
            "SH0.BAY10": {
                "capacity": 511587647488,
                "protocol": "SAS",
                "serial": "S0WZNEACB00266",
                "status": "healthy",
                "type": "SSD"
            }
        },
        "fans": {
            "CT0.FAN0": {
                "status": "ok"
            },
            "CT0.FAN1": {
                "status": "ok"
            },
            "CT0.FAN10": {
                "status": "ok"
            }
        },
        "interfaces": {
            "CT0.ETH0": {
                "speed": 1000000000,
                "status": "ok"
            },
            "CT0.ETH1": {
                "speed": 0,
                "status": "ok"
            },
            "CT0.FC0": {
                "speed": 8000000000,
                "status": "ok"
            },
            "CT1.IB1": {
                "speed": 56000000000,
                "status": "ok"
            },
            "CT1.SAS0": {
                "speed": 24000000000,
                "status": "ok"
            }
        },
        "power": {
            "CT0.PWR0": {
                "model": null,
                "serial": null,
                "status": "ok",
                "voltage": null
            },
            "CT0.PWR1": {
                "model": null,
                "serial": null,
                "status": "ok",
                "voltage": null
            }
        },
        "temps": {
            "CT0.TMP0": {
                "status": "ok",
                "temperature": 18
            },
            "CT0.TMP1": {
                "status": "ok",
                "temperature": 32
            }
        }
    }
'''


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.flasharray.plugins.module_utils.purefa import get_system, purefa_argument_spec


def generate_hardware_dict(array):
    hw_info = {'fans': {},
               'controllers': {},
               'temps': {},
               'drives': {},
               'interfaces': {},
               'power': {},
               }
    components = array.list_hardware()
    for component in range(0, len(components)):
        component_name = components[component]['name']
        if 'FAN' in component_name:
            fan_name = component_name
            hw_info['fans'][fan_name] = {'status': components[component]['status']}
        if 'PWR' in component_name:
            pwr_name = component_name
            hw_info['power'][pwr_name] = {'status': components[component]['status'],
                                          'voltage': components[component]['voltage'],
                                          'serial': components[component]['serial'],
                                          'model': components[component]['model']
                                          }
        if 'IB' in component_name:
            ib_name = component_name
            hw_info['interfaces'][ib_name] = {'status': components[component]['status'],
                                              'speed': components[component]['speed']
                                              }
        if 'SAS' in component_name:
            sas_name = component_name
            hw_info['interfaces'][sas_name] = {'status': components[component]['status'],
                                               'speed': components[component]['speed']
                                               }
        if 'ETH' in component_name:
            eth_name = component_name
            hw_info['interfaces'][eth_name] = {'status': components[component]['status'],
                                               'speed': components[component]['speed']
                                               }
        if 'FC' in component_name:
            eth_name = component_name
            hw_info['interfaces'][eth_name] = {'status': components[component]['status'],
                                               'speed': components[component]['speed']
                                               }
        if 'TMP' in component_name:
            tmp_name = component_name
            hw_info['temps'][tmp_name] = {'status': components[component]['status'],
                                          'temperature': components[component]['temperature']
                                          }
        if component_name in ['CT0', 'CT1']:
            cont_name = component_name
            hw_info['controllers'][cont_name] = {'status': components[component]['status'],
                                                 'serial': components[component]['serial'],
                                                 'model': components[component]['model']
                                                 }

    drives = array.list_drives()
    for drive in range(0, len(drives)):
        drive_name = drives[drive]['name']
        hw_info['drives'][drive_name] = {'capacity': drives[drive]['capacity'],
                                         'status': drives[drive]['status'],
                                         'protocol': drives[drive]['protocol'],
                                         'type': drives[drive]['type']
                                         }
        for disk in range(0, len(components)):
            if components[disk]['name'] == drive_name:
                hw_info['drives'][drive_name]['serial'] = components[disk]['serial']

    return hw_info


def main():
    argument_spec = purefa_argument_spec()

    module = AnsibleModule(argument_spec, supports_check_mode=True)
    array = get_system(module)

    module.exit_json(changed=False, purefa_info=generate_hardware_dict(array))


if __name__ == '__main__':
    main()
