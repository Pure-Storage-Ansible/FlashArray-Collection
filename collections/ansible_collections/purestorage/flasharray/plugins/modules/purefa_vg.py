#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2017, Simon Dodsley (simon@purestorage.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: purefa_vg
version_added: '2.9'
short_description: Manage volume groups on Pure Storage FlashArrays
description:
- Create, delete or modify volume groups on Pure Storage FlashArrays.
author:
- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
options:
  name:
    description:
    - The name of the volume group.
    type: str
    required: true
  state:
    description:
    - Define whether the volume group should exist or not.
    type: str
    default: present
    choices: [ absent, present ]
  eradicate:
    description:
    - Define whether to eradicate the volume group on delete and leave in trash.
    type : bool
    default: 'no'
  bw_qos:
    description:
    - Bandwidth limit for vgroup in M or G units.
      M will set MB/s
      G will set GB/s
      To clear an existing QoS setting use 0 (zero)
    type: str
  iops_qos:
    description:
    - IOPs limit for vgroup - use value or K or M
      K will mean 1000
      M will mean 1000000
      To clear an existing IOPs setting use 0 (zero)
    type: str
extends_documentation_fragment:
- purestorage.flasharray.purestorage.fa
'''

EXAMPLES = r'''
- name: Create new volune group
  purefa_vg:
    name: foo
    bw_qos: 50M
    iops_qos: 100
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
- name: Update volune group QoS limits
  purefa_vg:
    name: foo
    bw_qos: 0
    iops_qos: 5555
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
- name: Destroy volume group
  purefa_vg:
    name: foo
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
    state: absent
- name: Recover deleted volune group
  purefa_vg:
    name: foo
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
- name: Destroy and Eradicate volume group
  purefa_vg:
    name: foo
    eradicate: true
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
    state: absent
'''

RETURN = r'''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.flasharray.plugins.module_utils.purefa import get_system, purefa_argument_spec


VGROUP_API_VERSION = '1.13'
VG_IOPS_VERSION = '1.17'


def human_to_bytes(size):
    """Given a human-readable byte string (e.g. 2G, 30M),
       return the number of bytes.  Will return 0 if the argument has
       unexpected form.
    """
    bytes = size[:-1]
    unit = size[-1]
    if bytes.isdigit():
        bytes = int(bytes)
        if unit == 'P':
            bytes *= 1125899906842624
        elif unit == 'T':
            bytes *= 1099511627776
        elif unit == 'G':
            bytes *= 1073741824
        elif unit == 'M':
            bytes *= 1048576
        elif unit == 'K':
            bytes *= 1024
        else:
            bytes = 0
    else:
        bytes = 0
    return bytes


def human_to_real(iops):
    """Given a human-readable IOPs string (e.g. 2K, 30M),
       return the real number.  Will return 0 if the argument has
       unexpected form.
    """
    digit = iops[:-1]
    unit = iops[-1]
    if digit.isdigit():
        digit = int(digit)
        if unit == 'M':
            digit *= 1000000
        elif unit == 'K':
            digit *= 1000
        else:
            digit = 0
    else:
        digit = 0
    return digit


def get_pending_vgroup(module, array):
    """ Get Deleted Volume Group"""
    vgroup = None
    for vgrp in array.list_vgroups(pending=True):
        if vgrp["name"] == module.params['name'] and vgrp['time_remaining']:
            vgroup = vgrp
            break

    return vgroup


def get_vgroup(module, array):
    """ Get Volume Group"""
    vgroup = None
    for vgrp in array.list_vgroups():
        if vgrp["name"] == module.params['name']:
            vgroup = vgrp
            break

    return vgroup


def make_vgroup(module, array):
    """ Create Volume Group"""
    changed = True
    if not module.check_mode:
        api_version = array._list_available_rest_versions()
        if module.params['bw_qos'] or module.params['iops_qos'] and VG_IOPS_VERSION in api_version:
            if module.params['bw_qos'] and not module.params['iops_qos']:
                if 549755813888 >= int(human_to_bytes(module.params['bw_qos'])) >= 1048576:
                    try:
                        array.create_vgroup(module.params['name'],
                                            bandwidth_limit=module.params['bw_qos'])
                    except Exception:
                        module.fail_json(msg='Vgroup {0} creation failed.'.format(module.params['name']))
                else:
                    module.fail_json(msg='Bandwidth QoS value {0} out of range.'.format(module.params['bw_qos']))
            elif module.params['iops_qos'] and not module.params['bw_qos']:
                if 100000000 >= int(human_to_real(module.params['iops_qos'])) >= 100:
                    try:
                        array.create_vgroup(module.params['name'],
                                            iops_limit=module.params['iops_qos'])
                    except Exception:
                        module.fail_json(msg='Vgroup {0} creation failed.'.format(module.params['name']))
                else:
                    module.fail_json(msg='IOPs QoS value {0} out of range.'.format(module.params['iops_qos']))
            else:
                bw_qos_size = int(human_to_bytes(module.params['bw_qos']))
                if 100000000 >= int(human_to_real(module.params['iops_qos'])) >= 100 and 549755813888 >= bw_qos_size >= 1048576:
                    try:
                        array.create_vgroup(module.params['name'],
                                            iops_limit=module.params['iops_qos'],
                                            bandwidth_limit=module.params['bw_qos'])
                    except Exception:
                        module.fail_json(msg='Vgroup {0} creation failed.'.format(module.params['name']))
                else:
                    module.fail_json(msg='IOPs or Bandwidth QoS value out of range.')
        else:
            try:
                array.create_vgroup(module.params['name'])
            except Exception:
                module.fail_json(msg='creation of volume group {0} failed.'.format(module.params['name']))

    module.exit_json(changed=changed)


def update_vgroup(module, array):
    """ Update Volume Group"""
    changed = True
    if not module.check_mode:
        api_version = array._list_available_rest_versions()
        if VG_IOPS_VERSION in api_version:
            try:
                vg_qos = array.get_vgroup(module.params['name'], qos=True)
            except Exception:
                module.fail_json(msg='Failed to get QoS settings for vgroup {0}.'.format(module.params['name']))
        if VG_IOPS_VERSION in api_version:
            if vg_qos['bandwidth_limit'] is None:
                vg_qos['bandwidth_limit'] = 0
            if vg_qos['iops_limit'] is None:
                vg_qos['iops_limit'] = 0
        if module.params['bw_qos'] and VG_IOPS_VERSION in api_version:
            if human_to_bytes(module.params['bw_qos']) != vg_qos['bandwidth_limit']:
                if module.params['bw_qos'] == '0':
                    try:
                        array.set_volume(module.params['name'], bandwidth_limit='')
                    except Exception:
                        module.fail_json(msg='Vgroup {0} Bandwidth QoS removal failed.'.format(module.params['name']))
                elif 549755813888 >= int(human_to_bytes(module.params['bw_qos'])) >= 1048576:
                    try:
                        array.set_volume(module.params['name'], bandwidth_limit=module.params['bw_qos'])
                    except Exception:
                        module.fail_json(msg='Vgroup {0} Bandwidth QoS change failed.'.format(module.params['name']))
                else:
                    module.fail_json(msg='Bandwidth QoS value {0} out of range.'.format(module.params['bw_qos']))
        if module.params['iops_qos'] and VG_IOPS_VERSION in api_version:
            if human_to_real(module.params['iops_qos']) != vg_qos['iops_limit']:
                if module.params['iops_qos'] == '0':
                    try:
                        array.set_volume(module.params['name'], iops_limit='')
                    except Exception:
                        module.fail_json(msg='Vgroup {0} IOPs QoS removal failed.'.format(module.params['name']))
                elif 100000000 >= int(human_to_real(module.params['iops_qos'])) >= 100:
                    try:
                        array.set_volume(module.params['name'], iops_limit=module.params['iops_qos'])
                    except Exception:
                        module.fail_json(msg='Vgroup {0} IOPs QoS change failed.'.format(module.params['name']))
                else:
                    module.fail_json(msg='Bandwidth QoS value {0} out of range.'.format(module.params['bw_qos']))

    module.exit_json(changed=changed)


def recover_vgroup(module, array):
    """ Recover Volume Group"""
    changed = True
    if not module.check_mode:
        try:
            array.recover_vgroup(module.params['name'])
        except Exception:
            module.fail_json(msg='Recovery of volume group {0} failed.'.format(module.params['name']))

    module.exit_json(changed=changed)


def eradicate_vgroup(module, array):
    """ Eradicate Volume Group"""
    changed = True
    if not module.check_mode:
        try:
            array.eradicate_vgroup(module.params['name'])
        except Exception:
            module.fail_json(msg='Eradicating vgroup {0} failed.'.format(module.params['name']))
    module.exit_json(changed=changed)


def delete_vgroup(module, array):
    """ Delete Volume Group"""
    changed = True
    if not module.check_mode:
        try:
            array.destroy_vgroup(module.params['name'])
        except Exception:
            module.fail_json(msg='Deleting vgroup {0} failed.'.format(module.params['name']))
    if module.params['eradicate']:
        eradicate_vgroup(module, array)

    module.exit_json(changed=changed)


def main():
    argument_spec = purefa_argument_spec()
    argument_spec.update(dict(
        name=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['absent', 'present']),
        bw_qos=dict(type='str'),
        iops_qos=dict(type='str'),
        eradicate=dict(type='bool', default=False),
    ))

    module = AnsibleModule(argument_spec,
                           supports_check_mode=True)

    state = module.params['state']
    array = get_system(module)
    api_version = array._list_available_rest_versions()
    if VGROUP_API_VERSION not in api_version:
        module.fail_json(msg='API version does not support volume groups.')

    vgroup = get_vgroup(module, array)
    xvgroup = get_pending_vgroup(module, array)

    if xvgroup and state == 'present':
        recover_vgroup(module, array)
    elif vgroup and state == 'absent':
        delete_vgroup(module, array)
    elif xvgroup and state == 'absent' and module.params['eradicate']:
        eradicate_vgroup(module, array)
    elif not vgroup and not xvgroup and state == 'present':
        make_vgroup(module, array)
    elif vgroup and state == 'present':
        update_vgroup(module, array)
    elif vgroup is None and state == 'absent':
        module.exit_json(changed=False)

    module.exit_json(changed=False)


if __name__ == '__main__':
    main()
