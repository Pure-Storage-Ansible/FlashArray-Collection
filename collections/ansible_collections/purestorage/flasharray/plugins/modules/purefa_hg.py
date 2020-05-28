#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2018, Simon Dodsley (simon@purestorage.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: purefa_hg
version_added: '2.4'
short_description: Manage hostgroups on Pure Storage FlashArrays
description:
- Create, delete or modifiy hostgroups on Pure Storage FlashArrays.
author:
- Pure Storage ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
options:
  hostgroup:
    description:
    - The name of the hostgroup.
    type: str
    required: true
  state:
    description:
    - Define whether the hostgroup should exist or not.
    type: str
    default: present
    choices: [ absent, present ]
  host:
    type: list
    description:
    - List of existing hosts to add to hostgroup.
  volume:
    type: list
    description:
    - List of existing volumes to add to hostgroup.
  lun:
    description:
    - LUN ID to assign to volume for hostgroup. Must be unique.
    - Only applicable when only one volume is specified for connection.
    - If not provided the ID will be automatically assigned.
    - Range for LUN ID is 1 to 4095.
    type: int
extends_documentation_fragment:
- purestorage.flasharray.purestorage.fa
'''

EXAMPLES = r'''
- name: Create empty hostgroup
  purefa_hg:
    hostgroup: foo
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Add hosts and volumes to existing or new hostgroup
  purefa_hg:
    hostgroup: foo
    host:
      - host1
      - host2
    volume:
      - vol1
      - vol2
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Delete hosts and volumes from hostgroup
  purefa_hg:
    hostgroup: foo
    host:
      - host1
      - host2
    volume:
      - vol1
      - vol2
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
    state: absent

# This will disconnect all hosts and volumes in the hostgroup
- name: Delete hostgroup
  purefa_hg:
    hostgroup: foo
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
    state: absent

- name: Create host group with hosts and volumes
  purefa_hg:
    hostgroup: bar
    host:
      - host1
      - host2
    volume:
      - vol1
      - vol2
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
'''

RETURN = r'''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.flasharray.plugins.module_utils.purefa import get_system, purefa_argument_spec


def get_hostgroup(module, array):

    hostgroup = None

    for host in array.list_hgroups():
        if host["name"] == module.params['hostgroup']:
            hostgroup = host
            break

    return hostgroup


def make_hostgroup(module, array):

    changed = True
    if not module.check_mode:
        try:
            array.create_hgroup(module.params['hostgroup'])
        except Exception:
            module.fail_json(msg='Failed to create hostgroup {0}'.format(module.params['hostgroup']))
        if module.params['host']:
            array.set_hgroup(module.params['hostgroup'], hostlist=module.params['host'])
        if module.params['volume']:
            if len(module.params['volume']) == 1 and module.params['lun']:
                try:
                    array.connect_hgroup(module.params['hostgroup'], module.params['volume'][0], lun=module.params['lun'])
                except Exception:
                    module.fail_json(msg="Failed to add volume {0} with LUN ID {1}".format(module.params['volume'][0], module.params['lun']))
            else:
                for vol in module.params['volume']:
                    try:
                        array.connect_hgroup(module.params['hostgroup'], vol)
                    except Exception:
                        module.fail_json(msg='Failed to add volume to hostgroup')
    module.exit_json(changed=changed)


def update_hostgroup(module, array):
    changed = True
    if not module.check_mode:
        changed = False
        hgroup = get_hostgroup(module, array)
        volumes = array.list_hgroup_connections(module.params['hostgroup'])
        if module.params['state'] == "present":
            if module.params['host']:
                new_hosts = list(set(module.params['host']).difference(hgroup['hosts']))
                if new_hosts:
                    try:
                        array.set_hgroup(module.params['hostgroup'], addhostlist=new_hosts)
                        changed = True
                    except Exception:
                        module.fail_json(msg='Failed to add host(s) to hostgroup')
            if module.params['volume']:
                if volumes:
                    current_vols = [vol['vol'] for vol in volumes]
                    new_volumes = list(set(module.params['volume']).difference(set(current_vols)))
                    if len(new_volumes) == 1 and module.params['lun']:
                        try:
                            array.connect_hgroup(module.params['hostgroup'], new_volumes[0], lun=module.params['lun'])
                            changed = True
                        except Exception:
                            module.fail_json(msg="Failed to add volume {0} with LUN ID {1}".format(new_volumes[0], module.params['lun']))
                    else:
                        for cvol in new_volumes:
                            try:
                                array.connect_hgroup(module.params['hostgroup'], cvol)
                                changed = True
                            except Exception:
                                module.fail_json(msg='Failed to connect volume {0} to hostgroup {1}.'.format(cvol, module.params['hostgroup']))
                else:
                    if len(module.params['volume']) == 1 and module.params['lun']:
                        try:
                            array.connect_hgroup(module.params['hostgroup'], module.params['volume'][0], lun=module.params['lun'])
                            changed = True
                        except Exception:
                            module.fail_json(msg="Failed to add volume {0} with LUN ID {1}".format(module.params['volume'], module.params['lun']))
                    else:
                        for cvol in module.params['volume']:
                            try:
                                array.connect_hgroup(module.params['hostgroup'], cvol)
                                changed = True
                            except Exception:
                                module.fail_json(msg='Failed to connect volume {0} to hostgroup {1}.'.format(cvol, module.params['hostgroup']))
        else:
            if module.params['host']:
                old_hosts = list(set(module.params['host']).intersection(hgroup['hosts']))
                old_hosts = list(set(module.params['host']).intersection(hgroup['hosts']))
                if old_hosts:
                    try:
                        array.set_hgroup(module.params['hostgroup'], remhostlist=old_hosts)
                        changed = True
                    except Exception:
                        module.fail_json(msg='Failed to remove hosts {0} from hostgroup {1}'.format(old_hosts, module.params['hostgroup']))
            if module.params['volume']:
                old_volumes = list(set(module.params['volume']).difference(set([vol['name'] for vol in volumes])))
                for cvol in old_volumes:
                    try:
                        array.disconnect_hgroup(module.params['hostgroup'], cvol)
                        changed = True
                    except Exception:
                        module.fail_json(msg='Failed to disconnect volume {0} from hostgroup {1}'.format(cvol, module.params['hostgroup']))

    module.exit_json(changed=changed)


def delete_hostgroup(module, array):
    changed = True
    if not module.check_mode:
        try:
            vols = array.list_hgroup_connections(module.params['hostgroup'])
            for vol in vols:
                try:
                    array.disconnect_hgroup(module.params['hostgroup'], vol["vol"])
                except Exception:
                    module.fail_json(msg='Failed to disconnect volume {0} from hostgroup {1}'.format(vol["vol"], module.params['hostgroup']))
            host = array.get_hgroup(module.params['hostgroup'])
            try:
                array.set_hgroup(module.params['hostgroup'], remhostlist=host['hosts'])
                try:
                    array.delete_hgroup(module.params['hostgroup'])
                except Exception:
                    module.fail_json(msg='Failed to delete hostgroup {0}'.format(module.params['hostgroup']))
            except Exception:
                module.fail_json(msg='Failed to remove hosts {0} from hostgroup {1}'.format(host['hosts'], module.params['hostgroup']))
        except Exception:
            module.fail_json(msg='Failed to get volume connection for hostgroup {0}'.format(module.params['hostgroup']))
    module.exit_json(changed=changed)


def main():
    argument_spec = purefa_argument_spec()
    argument_spec.update(dict(
        hostgroup=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['absent', 'present']),
        host=dict(type='list'),
        lun=dict(type='int'),
        volume=dict(type='list'),
    ))

    module = AnsibleModule(argument_spec, supports_check_mode=True)

    state = module.params['state']
    array = get_system(module)
    if module.params['host'] is not None:
        new_hosts = [host.lower() for host in module.params['host']]
        module.params['host'] = new_hosts
    hostgroup = get_hostgroup(module, array)

    if module.params['host']:
        try:
            for hst in module.params['host']:
                array.get_host(hst)
        except Exception:
            module.fail_json(msg='Host {0} not found'.format(hst))
    if module.params['lun'] and len(module.params['volume']) > 1:
        module.fail_json(msg='LUN ID cannot be specified with multiple volumes.')

    if module.params['lun'] and not 1 <= module.params['lun'] <= 4095:
        module.fail_json(msg='LUN ID of {0} is out of range (1 to 4095)'.format(module.params['lun']))

    if module.params['volume']:
        try:
            for vol in module.params['volume']:
                array.get_volume(vol)
        except Exception:
            module.fail_json(msg='Volume {0} not found'.format(vol))

    if hostgroup and state == 'present':
        update_hostgroup(module, array)
    elif hostgroup and module.params['volume'] and state == 'absent':
        update_hostgroup(module, array)
    elif hostgroup and module.params['host'] and state == 'absent':
        update_hostgroup(module, array)
    elif hostgroup and state == 'absent':
        delete_hostgroup(module, array)
    elif hostgroup is None and state == 'absent':
        module.exit_json(changed=False)
    else:
        make_hostgroup(module, array)

    module.exit_json(changed=False)


if __name__ == '__main__':
    main()
