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
module: purefa_host
version_added: '1.0.0'
short_description: Manage hosts on Pure Storage FlashArrays
description:
- Create, delete or modify hosts on Pure Storage FlashArrays.
author:
- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
notes:
- If specifying C(lun) option ensure host support requested value
options:
  name:
    description:
    - The name of the host.
    type: str
    required: true
    aliases: [ host ]
  state:
    description:
    - Define whether the host should exist or not.
    - When removing host all connected volumes will be disconnected.
    type: str
    default: present
    choices: [ absent, present ]
  protocol:
    description:
    - Defines the host connection protocol for volumes.
    type: str
    default: iscsi
    choices: [ fc, iscsi, nvme, mixed ]
  wwns:
    type: list
    elements: str
    description:
    - List of wwns of the host if protocol is fc or mixed.
  iqn:
    type: list
    elements: str
    description:
    - List of IQNs of the host if protocol is iscsi or mixed.
  nqn:
    type: list
    elements: str
    description:
    - List of NQNs of the host if protocol is nvme or mixed.
  volume:
    type: str
    description:
    - Volume name to map to the host.
  lun:
    description:
    - LUN ID to assign to volume for host. Must be unique.
    - If not provided the ID will be automatically assigned.
    - Range for LUN ID is 1 to 4095.
    type: int
  personality:
    type: str
    description:
    - Define which operating system the host is. Recommended for
      ActiveCluster integration.
    default: ''
    choices: ['hpux', 'vms', 'aix', 'esxi', 'solaris', 'hitachi-vsp', 'oracle-vm-server', 'delete', '']
  preferred_array:
    type: list
    elements: str
    description:
    - List of preferred arrays in an ActiveCluster environment.
    - To remove existing preferred arrays from the host, specify I(delete).
  target_user:
    type: str
    description:
    - Sets the target user name for CHAP authentication
    - Required with I(target_password)
    - To clear the username/password pair use I(clear) as the password
  target_password:
    type: str
    description:
    - Sets the target password for CHAP authentication
    - Password length between 12 and 255 characters
    - To clear the username/password pair use I(clear) as the password
    - SETTING A PASSWORD IS NON-IDEMPOTENT
  host_user:
    type: str
    description:
    - Sets the host user name for CHAP authentication
    - Required with I(host_password)
    - To clear the username/password pair use I(clear) as the password
  host_password:
    type: str
    description:
    - Sets the host password for CHAP authentication
    - Password length between 12 and 255 characters
    - To clear the username/password pair use I(clear) as the password
    - SETTING A PASSWORD IS NON-IDEMPOTENT
extends_documentation_fragment:
- purestorage.flasharray.purestorage.fa
'''

EXAMPLES = r'''
- name: Create new AIX host
  purefa_host:
    host: foo
    personality: aix
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Delete host
  purefa_host:
    host: foo
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
    state: absent

- name: Make host bar with wwn ports
  purefa_host:
    host: bar
    protocol: fc
    wwns:
    - 00:00:00:00:00:00:00
    - 11:11:11:11:11:11:11
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Make host bar with iSCSI ports
  purefa_host:
    host: bar
    protocol: iscsi
    iqn:
    - iqn.1994-05.com.redhat:7d366003913
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Make host bar with NVMe ports
  purefa_host:
    host: bar
    protocol: nvme
    nqn:
    - nqn.2014-08.com.vendor:nvme:nvm-subsystem-sn-d78432
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Make mixed protocol host
  purefa_host:
    host: bar
    protocol: mixed
    nqn:
    - nqn.2014-08.com.vendor:nvme:nvm-subsystem-sn-d78432
    iqn:
    - iqn.1994-05.com.redhat:7d366003914
    wwns:
    - 00:00:00:00:00:00:01
    - 11:11:11:11:11:11:12
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Map host foo to volume bar as LUN ID 12
  purefa_host:
    host: foo
    volume: bar
    lun: 12
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Disconnect volume bar from host foo
  purefa_host:
    host: foo
    volume: bar
    state: absent
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Add preferred arrays to host foo
  purefa_host:
    host: foo
    preferred_array:
    - array1
    - array2
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Delete preferred arrays from host foo
  purefa_host:
    host: foo
    preferred_array: delete
    fa_url: 10.10.10.2

- name: Set CHAP target and host username/password pairs
  purefa_host:
    host: foo
    target_user: user1
    target_password: passwrodpassword
    host_user: user2
    host_password: passwrodpassword
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Delete CHAP target and host username/password pairs
  purefa_host:
    host: foo
    target_user: user
    target_password: clear
    host_user: user
    host_password: clear
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
'''

RETURN = r'''
'''

import re
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.flasharray.plugins.module_utils.purefa import get_system, purefa_argument_spec


AC_REQUIRED_API_VERSION = '1.14'
PREFERRED_ARRAY_API_VERSION = '1.15'
NVME_API_VERSION = '1.16'


def _is_cbs(array, is_cbs=False):
    """Is the selected array a Cloud Block Store"""
    model = array.get(controllers=True)[0]['model']
    is_cbs = bool('CBS' in model)
    return is_cbs


def _set_host_initiators(module, array):
    """Set host initiators."""
    if module.params['protocol'] in ['nvme', 'mixed']:
        if module.params['nqn']:
            try:
                array.set_host(module.params['name'],
                               nqnlist=module.params['nqn'])
            except Exception:
                module.fail_json(msg='Setting of NVMe NQN failed.')
    if module.params['protocol'] in ['iscsi', 'mixed']:
        if module.params['iqn']:
            try:
                array.set_host(module.params['name'],
                               iqnlist=module.params['iqn'])
            except Exception:
                module.fail_json(msg='Setting of iSCSI IQN failed.')
    if module.params['protocol'] in ['fc', 'mixed']:
        if module.params['wwns']:
            try:
                array.set_host(module.params['name'],
                               wwnlist=module.params['wwns'])
            except Exception:
                module.fail_json(msg='Setting of FC WWNs failed.')


def _update_host_initiators(module, array, answer=False):
    """Change host initiator if iscsi or nvme or add new FC WWNs"""
    if module.params['protocol'] in ['nvme', 'mixed']:
        if module.params['nqn']:
            current_nqn = array.get_host(module.params['name'])['nqn']
            if current_nqn != module.params['nqn']:
                try:
                    array.set_host(module.params['name'],
                                   nqnlist=module.params['nqn'])
                    answer = True
                except Exception:
                    module.fail_json(msg='Change of NVMe NQN failed.')
    if module.params['protocol'] in ['iscsi', 'mixed']:
        if module.params['iqn']:
            current_iqn = array.get_host(module.params['name'])['iqn']
            if current_iqn != module.params['iqn']:
                try:
                    array.set_host(module.params['name'],
                                   iqnlist=module.params['iqn'])
                    answer = True
                except Exception:
                    module.fail_json(msg='Change of iSCSI IQN failed.')
    if module.params['protocol'] in ['fc', 'mixed']:
        if module.params['wwns']:
            module.params['wwns'] = [wwn.replace(':', '') for wwn in module.params['wwns']]
            module.params['wwns'] = [wwn.upper() for wwn in module.params['wwns']]
            current_wwn = array.get_host(module.params['name'])['wwn']
            if current_wwn != module.params['wwns']:
                try:
                    array.set_host(module.params['name'],
                                   wwnlist=module.params['wwns'])
                    answer = True
                except Exception:
                    module.fail_json(msg='FC WWN change failed.')
    return answer


def _connect_new_volume(module, array, answer=False):
    """Connect volume to host"""
    api_version = array._list_available_rest_versions()
    if AC_REQUIRED_API_VERSION in api_version and module.params['lun']:
        try:
            array.connect_host(module.params['name'],
                               module.params['volume'],
                               lun=module.params['lun'])
            answer = True
        except Exception:
            module.fail_json(msg='LUN ID {0} invalid. Check for duplicate LUN IDs.'.format(module.params['lun']))
    else:
        array.connect_host(module.params['name'], module.params['volume'])
        answer = True
    return answer


def _disconnect_volume(module, array, answer=False):
    """Disconnect volume from host"""
    try:
        array.disconnect_host(module.params['name'], module.params['volume'])
        answer = True
    except Exception:
        module.fail_json(msg="Failed to disconnect volume {0}".format(module.params['volume']))
    return answer


def _set_host_personality(module, array):
    """Set host personality. Only called when supported"""
    if module.params['personality'] != 'delete':
        array.set_host(module.params['name'],
                       personality=module.params['personality'])
    else:
        array.set_host(module.params['name'], personality='')


def _set_preferred_array(module, array):
    """Set preferred array list. Only called when supported"""
    if module.params['preferred_array'] != ['delete']:
        array.set_host(module.params['name'],
                       preferred_array=module.params['preferred_array'])
    else:
        array.set_host(module.params['name'], personality='')


def _set_chap_security(module, array):
    """Set CHAP usernames and passwords"""
    pattern = re.compile("[^ ]{12,255}")
    if module.params['host_user']:
        if not pattern.match(module.params['host_password']):
            module.fail_json(msg='host_password must contain a minimum of 12 and a maximum of 255 characters')
        try:
            array.set_host(module.params['name'], host_user=module.params['host_user'],
                           host_password=module.params['host_password'])
        except Exception:
            module.params(msg='Failed to set CHAP host username and password')
    if module.params['target_user']:
        if not pattern.match(module.params['target_password']):
            module.fail_json(msg='target_password must contain a minimum of 12 and a maximum of 255 characters')
        try:
            array.set_host(module.params['name'], target_user=module.params['target_user'],
                           target_password=module.params['target_password'])
        except Exception:
            module.params(msg='Failed to set CHAP target username and password')


def _update_chap_security(module, array, answer=False):
    """Change CHAP usernames and passwords"""
    pattern = re.compile("[^ ]{12,255}")
    chap = array.get_host(module.params['name'], chap=True)
    if module.params['host_user']:
        if module.params['host_password'] == 'clear':
            if chap['host_user']:
                try:
                    array.set_host(module.params['name'], host_user="")
                    answer = True
                except Exception:
                    module.params(msg='Failed to clear CHAP host username and password')
        else:
            if not pattern.match(module.params['host_password']):
                module.fail_json(msg='host_password must contain a minimum of 12 and a maximum of 255 characters')
            try:
                array.set_host(module.params['name'], host_user=module.params['host_user'],
                               host_password=module.params['host_password'])
                answer = True
            except Exception:
                module.params(msg='Failed to set CHAP host username and password')
    if module.params['target_user']:
        if module.params['target_password'] == 'clear':
            if chap['target_user']:
                try:
                    array.set_host(module.params['name'], target_user="")
                    answer = True
                except Exception:
                    module.params(msg='Failed to clear CHAP target username and password')
        else:
            if not pattern.match(module.params['target_password']):
                module.fail_json(msg='target_password must contain a minimum of 12 and a maximum of 255 characters')
            try:
                array.set_host(module.params['name'], target_user=module.params['target_user'],
                               target_password=module.params['target_password'])
                answer = True
            except Exception:
                module.params(msg='Failed to set CHAP target username and password')
    return answer


def _update_host_personality(module, array, answer=False):
    """Change host personality. Only called when supported"""
    personality = array.get_host(module.params['name'], personality=True)['personality']
    if personality is None and module.params['personality'] != 'delete':
        try:
            array.set_host(module.params['name'],
                           personality=module.params['personality'])
            answer = True
        except Exception:
            module.fail_json(msg='Personality setting failed.')
    if personality is not None:
        if module.params['personality'] == 'delete':
            try:
                array.set_host(module.params['name'], personality='')
                answer = True
            except Exception:
                module.fail_json(msg='Personality deletion failed.')
        elif personality != module.params['personality']:
            try:
                array.set_host(module.params['name'],
                               personality=module.params['personality'])
                answer = True
            except Exception:
                module.fail_json(msg='Personality change failed.')
    return answer


def _update_preferred_array(module, array, answer=False):
    """Update existing preferred array list. Only called when supported"""
    preferred_array = array.get_host(module.params['name'], preferred_array=True)['preferred_array']
    if preferred_array == [] and module.params['preferred_array'] != ['delete']:
        try:
            array.set_host(module.params['name'],
                           preferred_array=module.params['preferred_array'])
            answer = True
        except Exception:
            module.fail_json(msg='Preferred array list creation failed for {0}.'.format(module.params['name']))
    elif preferred_array != []:
        if module.params['preferred_array'] == ['delete']:
            try:
                array.set_host(module.params['name'], preferred_array=[])
                answer = True
            except Exception:
                module.fail_json(msg='Preferred array list deletion failed for {0}.'.format(module.params['name']))
        elif preferred_array != module.params['preferred_array']:
            try:
                array.set_host(module.params['name'],
                               preferred_array=module.params['preferred_array'])
                answer = True
            except Exception:
                module.fail_json(msg='Preferred array list change failed for {0}.'.format(module.params['name']))
    return answer


def get_host(module, array):
    host = None
    for hst in array.list_hosts():
        if hst["name"] == module.params['name']:
            host = hst
            break
    return host


def make_host(module, array):
    changed = True
    if not module.check_mode:
        try:
            array.create_host(module.params['name'])
        except Exception:
            module.fail_json(msg='Host {0} creation failed.'.format(module.params['name']))
        try:
            _set_host_initiators(module, array)
            api_version = array._list_available_rest_versions()
            if AC_REQUIRED_API_VERSION in api_version and module.params['personality']:
                _set_host_personality(module, array)
            if PREFERRED_ARRAY_API_VERSION in api_version and module.params['preferred_array']:
                _set_preferred_array(module, array)
            if module.params['host_user'] or module.params['target_user']:
                _set_chap_security(module, array)
            if module.params['volume']:
                if module.params['lun']:
                    array.connect_host(module.params['name'],
                                       module.params['volume'],
                                       lun=module.params['lun'])
                else:
                    array.connect_host(module.params['name'], module.params['volume'])
        except Exception:
            module.fail_json(msg='Host {0} configuration failed.'.format(module.params['name']))
    module.exit_json(changed=changed)


def update_host(module, array):
    changed = True
    if not module.check_mode:
        if module.params['state'] == 'present':
            init_changed = vol_changed = pers_changed = pref_changed = chap_changed = False
            volumes = array.list_host_connections(module.params['name'])
            if module.params['iqn'] or module.params['wwns'] or module.params['nqn']:
                init_changed = _update_host_initiators(module, array)
            if module.params['volume']:
                current_vols = [vol['vol'] for vol in volumes]
                if not module.params['volume'] in current_vols:
                    vol_changed = _connect_new_volume(module, array)
            api_version = array._list_available_rest_versions()
            if AC_REQUIRED_API_VERSION in api_version:
                if module.params['personality']:
                    pers_changed = _update_host_personality(module, array)
            if PREFERRED_ARRAY_API_VERSION in api_version:
                if module.params['preferred_array']:
                    pref_changed = _update_preferred_array(module, array)
            if module.params['target_user'] or module.params['host_user']:
                chap_changed = _update_chap_security(module, array)
            changed = init_changed or vol_changed or pers_changed or pref_changed or chap_changed
        else:
            if module.params['volume']:
                volumes = array.list_host_connections(module.params['name'])
                current_vols = [vol['vol'] for vol in volumes]
                if module.params['volume'] in current_vols:
                    vol_changed = _disconnect_volume(module, array)
                else:
                    changed = False
    module.exit_json(changed=changed)


def delete_host(module, array):
    changed = True
    if not module.check_mode:
        try:
            for vol in array.list_host_connections(module.params['name']):
                array.disconnect_host(module.params['name'], vol["vol"])
            array.delete_host(module.params['name'])
        except Exception:
            module.fail_json(msg='Host {0} deletion failed'.format(module.params['name']))
    module.exit_json(changed=changed)


def main():
    argument_spec = purefa_argument_spec()
    argument_spec.update(dict(
        name=dict(type='str', required=True, aliases=['host']),
        state=dict(type='str', default='present', choices=['absent', 'present']),
        protocol=dict(type='str', default='iscsi', choices=['fc', 'iscsi', 'nvme', 'mixed']),
        nqn=dict(type='list', elements='str'),
        iqn=dict(type='list', elements='str'),
        wwns=dict(type='list', elements='str'),
        host_password=dict(type='str', no_log=True),
        host_user=dict(type='str'),
        target_password=dict(type='str', no_log=True),
        target_user=dict(type='str'),
        volume=dict(type='str'),
        lun=dict(type='int'),
        personality=dict(type='str', default='',
                         choices=['hpux', 'vms', 'aix', 'esxi', 'solaris',
                                  'hitachi-vsp', 'oracle-vm-server', 'delete', '']),
        preferred_array=dict(type='list', elements='str'),
    ))

    required_together = [['host_password', 'host_user'],
                         ['target_password', 'target_user']]

    module = AnsibleModule(argument_spec, supports_check_mode=True, required_together=required_together)

    array = get_system(module)
    module.params['name'] = module.params['name'].lower()
    pattern = re.compile("^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$")
    if not pattern.match(module.params['name']):
        module.fail_json(msg='Host name {0} does not conform to naming convention'.format(module.params['name']))
    if _is_cbs(array):
        if module.params['wwns'] or module.params['nqn']:
            module.fail_json(msg='Cloud Block Store only supports iSCSI as a protocol')
    api_version = array._list_available_rest_versions()
    if module.params['nqn'] is not None and NVME_API_VERSION not in api_version:
        module.fail_json(msg='NVMe protocol not supported. Please upgrade your array.')
    state = module.params['state']
    host = get_host(module, array)
    if module.params['lun'] and not 1 <= module.params['lun'] <= 4095:
        module.fail_json(msg='LUN ID of {0} is out of range (1 to 4095)'.format(module.params['lun']))
    if module.params['volume']:
        try:
            array.get_volume(module.params['volume'])
        except Exception:
            module.fail_json(msg='Volume {0} not found'.format(module.params['volume']))
    if module.params['preferred_array']:
        try:
            if module.params['preferred_array'] != ['delete']:
                all_connected_arrays = array.list_array_connections()
                if not all_connected_arrays:
                    module.fail_json(msg='No target arrays connected to source array - preferred arrays not possible.')
                else:
                    current_arrays = [array.get()['array_name']]
                    api_version = array._list_available_rest_versions()
                    if NVME_API_VERSION in api_version:
                        for current_array in range(0, len(all_connected_arrays)):
                            if all_connected_arrays[current_array]['type'] == "sync-replication":
                                current_arrays.append(all_connected_arrays[current_array]['array_name'])
                    else:
                        for current_array in range(0, len(all_connected_arrays)):
                            if all_connected_arrays[current_array]['type'] == ["sync-replication"]:
                                current_arrays.append(all_connected_arrays[current_array]['array_name'])
                for array_to_connect in range(0, len(module.params['preferred_array'])):
                    if module.params['preferred_array'][array_to_connect] not in current_arrays:
                        module.fail_json(msg='Array {0} is not a synchronously connected array.'.format(module.params['preferred_array'][array_to_connect]))
        except Exception:
            module.fail_json(msg='Failed to get existing array connections.')

    if host is None and state == 'present':
        make_host(module, array)
    elif host and state == 'present':
        update_host(module, array)
    elif host and state == 'absent' and module.params['volume']:
        update_host(module, array)
    elif host and state == 'absent':
        delete_host(module, array)
    elif host is None and state == 'absent':
        module.exit_json(changed=False)


if __name__ == '__main__':
    main()
