#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2019, Simon Dodsley (simon@purestorage.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: purefa_pod
short_description:  Manage AC pods in Pure Storage FlashArrays
description:
- Manage AC pods in a Pure Storage FlashArray.
author:
- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
options:
  name:
    description:
    - The name of the pod.
    type: str
    required: true
  stretch:
    description:
    - The name of the array to stretch to/unstretch from. Must be synchromously replicated.
    - To unstretch an array use state I(absent)
    - You can only specify a remote array, ie you cannot unstretch a pod from the
      current array and then restretch back to the current array.
    - To restretch a pod you must perform this from the remaining array the pod
      resides on.
    type: str
  failover:
    description:
    - The name of the array given priority to stay online if arrays loose
      contact with eachother.
    - Oprions are either array in the cluster, or I(auto)
    type: list
  state:
    description:
    - Define whether the pod should exist or not.
    default: present
    choices: [ absent, present ]
    type: str
  eradicate:
    description:
    - Define whether to eradicate the pod on delete or leave in trash.
    type: bool
    default: false
  target:
    description:
    - Name of clone target pod.
    type: str
  mediator:
    description:
    - Name of the mediator to use for a pod
    type: str
    default: purestorage
extends_documentation_fragment:
- purestorage.flasharray.purestorage.fa
'''

EXAMPLES = r'''
- name: Create new pod named foo
  purefa_pod:
    name: foo
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
    state: present

- name: Delete and eradicate pod named foo
  purefa_pod:
    name: foo
    eradicate: yes
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
    state: absent

- name: Set failover array for pod named foo
  purefa_pod:
    name: foo
    failover:
    - array1
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Set mediator for pod named foo
  purefa_pod:
    name: foo
    mediator: bar
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Stretch a pod named foo to array2
  purefa_pod:
    name: foo
    stretch: array2
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Unstretch a pod named foo from array2
  purefa_pod:
    name: foo
    stretch: array2
    state: absent
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Create clone of pod foo named bar
  purefa_pod:
    name: foo
    target: bar
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
    state: present
'''

RETURN = r'''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.flasharray.plugins.module_utils.purefa import get_system, purefa_argument_spec


POD_API_VERSION = "1.13"


def get_pod(module, array):
    """Return Pod or None"""
    try:
        return array.get_pod(module.params['name'])
    except Exception:
        return None


def get_target(module, array):
    """Return Pod or None"""
    try:
        return array.get_pod(module.params['target'])
    except Exception:
        return None


def get_destroyed_pod(module, array):
    """Return Destroyed Volume or None"""
    try:
        return bool(array.get_pod(module.params['name'], pending=True)['time_remaining'] != '')
    except Exception:
        return False


def get_destroyed_target(module, array):
    """Return Destroyed Volume or None"""
    try:
        return bool(array.get_pod(module.params['target'], pending=True)['time_remaining'] != '')
    except Exception:
        return False


def check_arrays(module, array):
    """Check if array name provided are sync-replicated"""
    good_arrays = []
    good_arrays.append(array.get()['array_name'])
    connected_arrays = array.list_array_connections()
    for arr in range(0, len(connected_arrays)):
        if connected_arrays[arr]['type'] == 'sync-replication':
            good_arrays.append(connected_arrays[arr]['array_name'])
    if module.params['failover'] is not None:
        if module.params['failover'] == ['auto']:
            failover_array = []
        else:
            failover_array = module.params['failover']
        if failover_array != []:
            for arr in range(0, len(failover_array)):
                if failover_array[arr] not in good_arrays:
                    module.fail_json(msg='Failover array {0} is not valid.'.format(failover_array[arr]))
    if module.params['stretch'] is not None:
        if module.params['stretch'] not in good_arrays:
            module.fail_json(msg='Stretch: Array {0} is not connected.'.format(module.params['stretch']))
    return None


def create_pod(module, array):
    """Create Pod"""
    changed = True
    if not module.check_mode:
        if module.params['target']:
            module.fail_json(msg='Cannot clone non-existant pod.')
        try:
            if module.params['failover']:
                array.create_pod(module.params['name'], failover_list=module.params['failover'])
            else:
                array.create_pod(module.params['name'])
        except Exception:
            module.fail_json(msg='Pod {0} creation failed.'.format(module.params['name']))
        if module.params['mediator'] != 'purestorage':
            try:
                array.set_pod(module.params['name'], mediator=module.params['mediator'])
            except Exception:
                module.warn('Failed to communicate with mediator {0}, using default value'.format(module.params['mediator']))
        if module.params['stretch']:
            current_array = array.get()['array_name']
            if module.params['stretch'] != current_array:
                try:
                    array.add_pod(module.params['name'], module.params['rrays'])
                except Exception:
                    module.fail_json(msg='Failed to stretch pod {0} to array {1}.'.format(module.params['name'],
                                                                                          module.params['stretch']))
    module.exit_json(changed=changed)


def clone_pod(module, array):
    """Create Pod Clone"""
    changed = True
    if not module.check_mode:
        changed = False
        if get_target(module, array) is None:
            if not get_destroyed_target(module, array):
                try:
                    array.clone_pod(module.params['name'],
                                    module.params['target'])
                    changed = True
                except Exception:
                    module.fail_json(msg='Clone pod {0} to pod {1} failed.'.format(module.params['name'],
                                                                                   module.params['target']))
            else:
                module.fail_json(msg='Target pod {0} already exists but deleted.'.format(module.params['target']))

    module.exit_json(changed=changed)


def update_pod(module, array):
    """Update Pod configuration"""
    changed = True
    if not module.check_mode:
        changed = False
        current_config = array.get_pod(module.params['name'], failover_preference=True)
        if module.params['failover']:
            current_failover = current_config['failover_preference']
            if current_failover == [] or sorted(module.params['failover']) != sorted(current_failover):
                try:
                    if module.params['failover'] == ['auto']:
                        if current_failover != []:
                            array.set_pod(module.params['name'], failover_preference=[])
                            changed = True
                    else:
                        array.set_pod(module.params['name'], failover_preference=module.params['failover'])
                        changed = True
                except Exception:
                    module.fail_json(msg='Failed to set failover preference for pod {0}.'.format(module.params['name']))
        current_config = array.get_pod(module.params['name'], mediator=True)
        if current_config['mediator'] != module.params['mediator']:
            try:
                array.set_pod(module.params['name'], mediator=module.params['mediator'])
                changed = True
            except Exception:
                module.warn('Failed to communicate with mediator {0}. Setting unchanged.'.format(module.params['mediator']))
    module.exit_json(changed=changed)


def stretch_pod(module, array):
    """Stretch/unstretch Pod configuration"""
    changed = True
    if not module.check_mode:
        changed = False
        current_config = array.get_pod(module.params['name'], failover_preference=True)
        if module.params['stretch']:
            current_arrays = []
            for arr in range(0, len(current_config['arrays'])):
                current_arrays.append(current_config['arrays'][arr]['name'])
            if module.params['stretch'] not in current_arrays and module.params['state'] == 'present':
                try:
                    array.add_pod(module.params['name'], module.params['stretch'])
                    changed = True
                except Exception:
                    module.fail_json(msg="Failed to stretch pod {0} to array {1}.".format(module.params['name'],
                                                                                          module.params['stretch']))

            if module.params['stretch'] in current_arrays and module.params['state'] == 'absent':
                try:
                    array.remove_pod(module.params['name'], module.params['stretch'])
                    changed = True
                except Exception:
                    module.fail_json(msg="Failed to unstretch pod {0} from array {1}.".format(module.params['name'],
                                                                                              module.params['stretch']))

    module.exit_json(changed=changed)


def delete_pod(module, array):
    """ Delete Pod"""
    changed = True
    if not module.check_mode:
        try:
            array.destroy_pod(module.params['name'])
            if module.params['eradicate']:
                try:
                    array.eradicate_pod(module.params['name'])
                except Exception:
                    module.fail_json(msg='Eradicate pod {0} failed.'.format(module.params['name']))
        except Exception:
            module.fail_json(msg='Delete pod {0} failed.'.format(module.params['name']))
    module.exit_json(changed=changed)


def eradicate_pod(module, array):
    """ Eradicate Deleted Pod"""
    changed = True
    if not module.check_mode:
        if module.params['eradicate']:
            try:
                array.eradicate_pod(module.params['name'])
            except Exception:
                module.fail_json(msg='Eradication of pod {0} failed'.format(module.params['name']))
    module.exit_json(changed=changed)


def recover_pod(module, array):
    """ Recover Deleted Pod"""
    changed = True
    if not module.check_mode:
        try:
            array.recover_pod(module.params['name'])
        except Exception:
            module.fail_json(msg='Recovery of pod {0} failed'.format(module.params['name']))
    module.exit_json(changed=changed)


def main():
    argument_spec = purefa_argument_spec()
    argument_spec.update(dict(
        name=dict(type='str', required=True),
        stretch=dict(type='str'),
        target=dict(type='str'),
        mediator=dict(type='str', default='purestorage'),
        failover=dict(type='list'),
        eradicate=dict(type='bool', default=False),
        state=dict(type='str', default='present', choices=['absent', 'present']),
    ))

    mutually_exclusive = [['stretch', 'failover'],
                          ['stretch', 'eradicate'],
                          ['stretch', 'mediator'],
                          ['target', 'mediator'],
                          ['target', 'stretch'],
                          ['target', 'failover'],
                          ['target', 'eradicate']]

    module = AnsibleModule(argument_spec,
                           mutually_exclusive=mutually_exclusive,
                           supports_check_mode=True)

    state = module.params['state']
    array = get_system(module)

    api_version = array._list_available_rest_versions()
    if POD_API_VERSION not in api_version:
        module.fail_json(msg='FlashArray REST version not supported. '
                             'Minimum version required: {0}'.format(POD_API_VERSION))

    pod = get_pod(module, array)
    destroyed = ''
    if not pod:
        destroyed = get_destroyed_pod(module, array)
    if module.params['failover'] or module.params['failover'] != 'auto':
        check_arrays(module, array)

    if state == 'present' and not pod:
        create_pod(module, array)
    elif pod and module.params['stretch']:
        stretch_pod(module, array)
    elif state == 'present' and pod and module.params['target']:
        clone_pod(module, array)
    elif state == 'present' and pod and module.params['target']:
        clone_pod(module, array)
    elif state == 'present' and pod:
        update_pod(module, array)
    elif state == 'absent' and pod and not module.params['stretch']:
        delete_pod(module, array)
    elif state == 'present' and destroyed:
        recover_pod(module, array)
    elif state == 'absent' and destroyed:
        eradicate_pod(module, array)
    elif state == 'absent' and not pod:
        module.exit_json(changed=False)


if __name__ == '__main__':
    main()
