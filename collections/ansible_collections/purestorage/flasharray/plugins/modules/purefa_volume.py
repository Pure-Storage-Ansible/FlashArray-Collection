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
module: purefa_volume
version_added: '2.4'
short_description:  Manage volumes on Pure Storage FlashArrays
description:
- Create, delete or extend the capacity of a volume on Pure Storage FlashArray.
author:
- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
options:
  name:
    description:
    - The name of the volume.
    type: str
    required: true
  target:
    description:
    - The name of the target volume, if copying.
    type: str
  state:
    description:
    - Define whether the volume should exist or not.
    default: present
    choices: [ absent, present ]
    type: str
  eradicate:
    description:
    - Define whether to eradicate the volume on delete or leave in trash.
    type: bool
    default: 'no'
  overwrite:
    description:
    - Define whether to overwrite a target volume if it already exisits.
    type: bool
    default: 'no'
  size:
    description:
    - Volume size in M, G, T or P units.
    type: str
  bw_qos:
    description:
    - Bandwidth limit for volume in M or G units.
      M will set MB/s
      G will set GB/s
      To clear an existing QoS setting use 0 (zero)
    version_added: '2.8'
    type: str
    aliases: [ qos ]
  iops_qos:
    description:
    - IOPs limit for volume - use value or K or M
      K will mean 1000
      M will mean 1000000
      To clear an existing IOPs setting use 0 (zero)
    version_added: '2.9'
    type: str
  move:
    description:
    - Move a volume in and out of a pod or vgroup
    - Provide the name of pod or vgroup to move the volume to
    - Pod and Vgroup names must be unique in the array
    - To move to the local array, specify C(local)
    - This is not idempotent - use C(ignore_errors) in the play
    type: str
  rename:
    description:
    - Value to rename the specified volume to.
    - Rename only applies to the container the current volumes is in.
    - There is no requirement to specify the pod or vgroup name as this is implied.
    type: str
extends_documentation_fragment:
- purestorage.flasharray.purestorage.fa
'''

EXAMPLES = r'''
- name: Create new volume named foo with a QoS limit
  purefa_volume:
    name: foo
    size: 1T
    bw_qos: 58M
    iops_qos: 23K
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
    state: present

- name: Extend the size of an existing volume named foo
  purefa_volume:
    name: foo
    size: 2T
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
    state: present

- name: Delete and eradicate volume named foo
  purefa_volume:
    name: foo
    eradicate: yes
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
    state: absent

- name: Create clone of volume bar named foo
  purefa_volume:
    name: foo
    target: bar
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
    state: present

- name: Overwrite volume bar with volume foo
  purefa_volume:
    name: foo
    target: bar
    overwrite: yes
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
    state: present

- name: Clear volume QoS from volume foo
  purefa_volume:
    name: foo
    bw_qos: 0
    iops_qos: 0
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
    state: present

- name: Move local volume foo from local array to pod bar
  purefa_volume:
    name: foo
    move: bar
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Move volume foo in pod bar to local array
  purefa_volume:
    name: bar::foo
    move: local
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Move volume foo in pod bar to vgroup fin
  purefa_volume:
    name: bar::foo
    move: fin
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
'''

RETURN = r'''
volume:
    description: A dictionary describing the changed volume.  Only some
        attributes below will be returned with various actions.
    type: dict
    returned: success
    contains:
        source:
            description: Volume name of source volume used for volume copy
            type: str
        serial:
            description: Volume serial number
            type: str
            sample: '361019ECACE43D83000120A4'
        created:
            description: Volume creation time
            type: str
            sample: '2019-03-13T22:49:24Z'
        name:
            description: Volume name
            type: str
        size:
            description: Volume size in bytes
            type: int
        bandwidth_limit:
            description: Volume bandwidth limit in bytes/sec
            type: int
        iops_limit:
            description: Volume IOPs limit
            type: int
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.flasharray.plugins.module_utils.purefa import get_system, purefa_argument_spec


QOS_API_VERSION = "1.14"
VGROUPS_API_VERSION = "1.13"
POD_API_VERSION = "1.13"
IOPS_API_VERSION = "1.17"


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


def get_volume(module, array):
    """Return Volume or None"""
    try:
        return array.get_volume(module.params['name'])
    except Exception:
        return None


def get_endpoint(name, array):
    """Return Endpoint or None"""
    try:
        return array.get_volume(name, pending=True, protocol_endpoint=True)
    except Exception:
        return None


def get_destroyed_volume(vol, array):
    """Return Destroyed Volume or None"""
    try:
        return bool(array.get_volume(vol, pending=True)['time_remaining'] != '')
    except Exception:
        return False


def get_destroyed_endpoint(vol, array):
    """Return Destroyed Endpoint or None"""
    try:
        return bool(array.get_volume(vol, protocol_endpoint=True, pending=True)['time_remaining'] != '')
    except Exception:
        return False


def get_target(module, array):
    """Return Volume or None"""
    try:
        return array.get_volume(module.params['target'])
    except Exception:
        return None


def check_vgroup(module, array):
    """Check is the requested VG to create volume in exists"""
    vg_exists = False
    api_version = array._list_available_rest_versions()
    if VGROUPS_API_VERSION in api_version:
        vg_name = module.params["name"].split("/")[0]
        try:
            vgs = array.list_vgroups()
        except Exception:
            module.fail_json(msg="Failed to get volume groups list. Check array.")
        for vgroup in range(0, len(vgs)):
            if vg_name == vgs[vgroup]['name']:
                vg_exists = True
                break
    else:
        module.fail_json(msg="VG volumes are not supported. Please upgrade your FlashArray.")
    return vg_exists


def check_pod(module, array):
    """Check is the requested pod to create volume in exists"""
    pod_exists = False
    api_version = array._list_available_rest_versions()
    if POD_API_VERSION in api_version:
        pod_name = module.params["name"].split("::")[0]
        try:
            pods = array.list_pods()
        except Exception:
            module.fail_json(msg="Failed to get pod list. Check array.")
        for pod in range(0, len(pods)):
            if pod_name == pods[pod]['name']:
                pod_exists = True
                break
    else:
        module.fail_json(msg="Pod volumes are not supported. Please upgrade your FlashArray.")
    return pod_exists


def create_volume(module, array):
    """Create Volume"""
    changed = True
    if not module.check_mode:
        if "/" in module.params['name'] and not check_vgroup(module, array):
            module.fail_json(msg="Failed to create volume {0}. Volume Group does not exist.".format(module.params["name"]))
        if "::" in module.params['name'] and not check_pod(module, array):
            module.fail_json(msg="Failed to create volume {0}. Pod does not exist".format(module.params["name"]))
        volfact = []
        api_version = array._list_available_rest_versions()
        if module.params['bw_qos'] or module.params['iops_qos']:
            if module.params['bw_qos'] and QOS_API_VERSION in api_version or module.params['iops_qos'] and IOPS_API_VERSION in api_version:
                if module.params['bw_qos'] and not module.params['iops_qos']:
                    if 549755813888 >= int(human_to_bytes(module.params['bw_qos'])) >= 1048576:
                        try:
                            volfact = array.create_volume(module.params['name'],
                                                          module.params['size'],
                                                          bandwidth_limit=module.params['bw_qos'])
                        except Exception:
                            module.fail_json(msg='Volume {0} creation failed.'.format(module.params['name']))
                    else:
                        module.fail_json(msg='Bandwidth QoS value {0} out of range.'.format(module.params['bw_qos']))
                elif module.params['iops_qos'] and not module.params['bw_qos']:
                    if 100000000 >= int(human_to_real(module.params['iops_qos'])) >= 100:
                        try:
                            volfact = array.create_volume(module.params['name'],
                                                          module.params['size'],
                                                          iops_limit=module.params['iops_qos'])
                        except Exception:
                            module.fail_json(msg='Volume {0} creation failed.'.format(module.params['name']))
                    else:
                        module.fail_json(msg='IOPs QoS value {0} out of range.'.format(module.params['iops_qos']))
                else:
                    bw_qos_size = int(human_to_bytes(module.params['bw_qos']))
                    if 100000000 >= int(human_to_real(module.params['iops_qos'])) >= 100 and 549755813888 >= bw_qos_size >= 1048576:
                        try:
                            volfact = array.create_volume(module.params['name'],
                                                          module.params['size'],
                                                          iops_limit=module.params['iops_qos'],
                                                          bandwidth_limit=module.params['bw_qos'])
                        except Exception:
                            module.fail_json(msg='Volume {0} creation failed.'.format(module.params['name']))
                    else:
                        module.fail_json(msg='IOPs or Bandwidth QoS value out of range.')

        else:
            try:
                if module.params['size']:
                    volfact = array.create_volume(module.params['name'], module.params['size'])
                else:
                    module.fail_json(msg='Size for a new volume must be specified')
            except Exception:
                module.fail_json(msg='Volume {0} creation failed.'.format(module.params['name']))

    module.exit_json(changed=changed, volume=volfact)


def copy_from_volume(module, array):
    """Create Volume Clone"""
    changed = True
    if not module.check_mode:
        volfact = []
        tgt = get_target(module, array)

        if tgt is None:
            try:
                volfact = array.copy_volume(module.params['name'],
                                            module.params['target'])
            except Exception:
                module.fail_json(msg='Copy volume {0} to volume {1} failed.'.format(module.params['name'],
                                                                                    module.params['target']))
        elif tgt is not None and module.params['overwrite']:
            try:
                volfact = array.copy_volume(module.params['name'],
                                            module.params['target'],
                                            overwrite=module.params['overwrite'])
            except Exception:
                module.fail_json(msg='Copy volume {0} to volume {1} failed.'.format(module.params['name'],
                                                                                    module.params['target']))

    module.exit_json(changed=changed, volume=volfact)


def update_volume(module, array):
    """Update Volume size and/or QoS"""
    changed = True
    if not module.check_mode:
        change = False
        volfact = []
        api_version = array._list_available_rest_versions()
        vol = array.get_volume(module.params['name'])
        vol_qos = array.get_volume(module.params['name'], qos=True)
        if QOS_API_VERSION in api_version:
            if vol_qos['bandwidth_limit'] is None:
                vol_qos['bandwidth_limit'] = 0
        if IOPS_API_VERSION in api_version:
            if vol_qos['iops_limit'] is None:
                vol_qos['iops_limit'] = 0
        if module.params['size']:
            if human_to_bytes(module.params['size']) != vol['size']:
                if human_to_bytes(module.params['size']) > vol['size']:
                    try:
                        volfact = array.extend_volume(module.params['name'], module.params['size'])
                        change = True
                    except Exception:
                        module.fail_json(msg='Volume {0} resize failed.'.format(module.params['name']))
        if module.params['bw_qos'] and QOS_API_VERSION in api_version:
            if human_to_bytes(module.params['bw_qos']) != vol_qos['bandwidth_limit']:
                if module.params['bw_qos'] == '0':
                    try:
                        volfact = array.set_volume(module.params['name'], bandwidth_limit='')
                        change = True
                    except Exception:
                        module.fail_json(msg='Volume {0} Bandwidth QoS removal failed.'.format(module.params['name']))
                elif 549755813888 >= int(human_to_bytes(module.params['bw_qos'])) >= 1048576:
                    try:
                        volfact = array.set_volume(module.params['name'],
                                                   bandwidth_limit=module.params['bw_qos'])
                        change = True
                    except Exception:
                        module.fail_json(msg='Volume {0} Bandwidth QoS change failed.'.format(module.params['name']))
                else:
                    module.fail_json(msg='Bandwidth QoS value {0} out of range.'.format(module.params['bw_qos']))
        if module.params['iops_qos'] and IOPS_API_VERSION in api_version:
            if human_to_real(module.params['iops_qos']) != vol_qos['iops_limit']:
                if module.params['iops_qos'] == '0':
                    try:
                        volfact = array.set_volume(module.params['name'], iops_limit='')
                        change = True
                    except Exception:
                        module.fail_json(msg='Volume {0} IOPs QoS removal failed.'.format(module.params['name']))
                elif 100000000 >= int(human_to_real(module.params['iops_qos'])) >= 100:
                    try:
                        volfact = array.set_volume(module.params['name'],
                                                   iops_limit=module.params['iops_qos'])
                        change = True
                    except Exception:
                        module.fail_json(msg='Volume {0} IOPs QoS change failed.'.format(module.params['name']))
                else:
                    module.fail_json(msg='Bandwidth QoS value {0} out of range.'.format(module.params['bw_qos']))

        module.exit_json(changed=change, volume=volfact)

    module.exit_json(changed=changed)


def rename_volume(module, array):
    """Rename volume within a container, ie pod, vgroup or local array"""
    changed = True
    if not module.check_mode:
        changed = False
        pod_name = ''
        vgroup_name = ''
        volfact = []
        target_name = module.params['rename']
        target_exists = False
        if "::" in module.params['name']:
            pod_name = module.params["name"].split("::")[0]
            target_name = pod_name + "::" + module.params['rename']
            try:
                array.get_volume(target_name, pending=True)
                target_exists = True
            except Exception:
                target_exists = False
        elif "/" in module.params['name']:
            vgroup_name = module.params["name"].split("/")[0]
            target_name = vgroup_name + "/" + module.params['rename']
            try:
                array.get_volume(target_name, pending=True)
                target_exists = True
            except Exception:
                target_exists = False
        else:
            try:
                array.get_volume(target_name, pending=True)
                target_exists = True
            except Exception:
                target_exists = False
        if target_exists and get_endpoint(target_name, array):
            module.fail_json(msg='Target volume {0} is a protocol-endpoinnt'.format(target_name))
        if not target_exists:
            if get_destroyed_endpoint(target_name, array):
                module.fail_json(msg='Target volume {0} is a destroyed protocol-endpoinnt'.format(target_name))
            else:
                try:
                    volfact = array.rename_volume(module.params["name"], module.params['rename'])
                    changed = True
                except Exception:
                    module.fail_json(msg='Rename volume {0} to {1} failed.'.format(module.params["name"], module.params['rename']))
        else:
            module.fail_json(msg="Target volume {0} already exists.".format(target_name))

    module.exit_json(changed=changed, volume=volfact)


def move_volume(module, array):
    """Move volume between pods, vgroups or local array"""
    changed = True
    if not module.check_mode:
        changed = False
        vgroup_exists = False
        pod_exists = False
        pod_name = ''
        vgroup_name = ''
        volfact = []
        volume_name = module.params['name']
        if "::" in module.params['name']:
            volume_name = module.params["name"].split("::")[1]
            pod_name = module.params["name"].split("::")[0]
        if "/" in module.params['name']:
            volume_name = module.params["name"].split("/")[1]
            vgroup_name = module.params["name"].split("/")[0]
        if module.params['move'] == 'local':
            target_location = ""
            if "::" not in module.params['name']:
                if "/" not in module.params['name']:
                    module.fail_json(msg='Source and destination [local] cannot be the same.')
            try:
                target_exists = array.get_volume(volume_name, pending=True)
            except Exception:
                target_exists = False
            if target_exists:
                module.fail_json(msg='Target volume {0} already exists'.format(volume_name))
        else:
            try:
                pod_exists = array.get_pod(module.params['move'])
                if len(pod_exists['arrays']) > 1:
                    module.fail_json(msg='Volume cannot be moved into a stretched pod')
                try:
                    target_exists = array.get_volume(module.params['move'] + "::" + volume_name, pending=True)
                    module.exit_json(changed=changed)
                except Exception:
                    target_exists = False
            except Exception:
                pod_exists = False
            try:
                vgroup_exists = bool(array.get_vgroup(module.params['move']))
                try:
                    target_exists = array.get_volume(module.params['move'] + "/" + volume_name, pending=True)
                    module.exit_json(changed=changed)
                except Exception:
                    target_exists = False
            except Exception:
                vgroup_exists = False
            if pod_exists and vgroup_exists:
                module.fail_json(msg='Move location {0} matches both a pod and a vgroup. Please rename one of these.'.format(module.params['move']))
            if not pod_exists and not vgroup_exists:
                module.fail_json(msg='Move location {0} does not exist.'.format(module.params['move']))
            if "::" in module.params['name']:
                if len(array.get_pod(module.params['move'])['arrays']) > 1:
                    module.fail_json(msg='Volume cannot be moved out of a stretched pod')
            if "/" in module.params['name']:
                if vgroup_name == module.params['move'] or pod_name == module.params['move']:
                    module.fail_json(msg='Source and destination cannot be the same')
            target_location = module.params['move']
        if get_endpoint(target_location, array):
            module.fail_json(msg='Target volume {0} is a protocol-endpoinnt'.format(target_location))
        try:
            volfact = array.move_volume(module.params['name'], target_location)
            changed = True
        except Exception:
            module.fail_json(msg='Move of volume {0} to {1} failed.'.format(module.params['name'],
                                                                            target_location))
    module.exit_json(changed=changed, volume=volfact)


def delete_volume(module, array):
    """ Delete Volume"""
    changed = True
    if not module.check_mode:
        volfact = []
        try:
            array.destroy_volume(module.params['name'])
            if module.params['eradicate']:
                try:
                    volfact = array.eradicate_volume(module.params['name'])
                except Exception:
                    module.fail_json(msg='Eradicate volume {0} failed.'.format(module.params['name']))
        except Exception:
            module.fail_json(msg='Delete volume {0} failed.'.format(module.params['name']))
    module.exit_json(changed=changed, volume=volfact)


def eradicate_volume(module, array):
    """ Eradicate Deleted Volume"""
    changed = True
    if not module.check_mode:
        volfact = []
        if module.params['eradicate']:
            try:
                array.eradicate_volume(module.params['name'])
            except Exception:
                module.fail_json(msg='Eradication of volume {0} failed'.format(module.params['name']))
    module.exit_json(changed=changed, volume=volfact)


def recover_volume(module, array):
    """ Recover Deleted Volume"""
    changed = True
    if not module.check_mode:
        volfact = []
        try:
            array.recover_volume(module.params['name'])
        except Exception:
            module.fail_json(msg='Recovery of volume {0} failed'.format(module.params['name']))
    module.exit_json(changed=changed, volume=volfact)


def main():
    argument_spec = purefa_argument_spec()
    argument_spec.update(dict(
        name=dict(type='str', required=True),
        target=dict(type='str'),
        move=dict(type='str'),
        rename=dict(type='str'),
        overwrite=dict(type='bool', default=False),
        eradicate=dict(type='bool', default=False),
        state=dict(type='str', default='present', choices=['absent', 'present']),
        bw_qos=dict(type='str', aliases=['qos']),
        iops_qos=dict(type='str'),
        size=dict(type='str'),
    ))

    mutually_exclusive = [['size', 'target'],
                          ['move', 'rename', 'target', 'eradicate'],
                          ['rename', 'move', 'target', 'eradicate']]

    module = AnsibleModule(argument_spec,
                           mutually_exclusive=mutually_exclusive,
                           supports_check_mode=True)

    size = module.params['size']
    bw_qos = module.params['bw_qos']
    iops_qos = module.params['iops_qos']
    state = module.params['state']
    destroyed = False
    array = get_system(module)
    volume = get_volume(module, array)
    endpoint = get_endpoint(module.params['name'], array)

    if endpoint:
        module.fail_json(msg='Volume {0} is an endpoint. Use purefa_endpoint module.'.format(module.params['name']))

    if not volume:
        destroyed = get_destroyed_volume(module.params['name'], array)
    target = get_target(module, array)

    if state == 'present' and not volume and not destroyed and size:
        create_volume(module, array)
    elif state == 'present' and volume and (size or bw_qos or iops_qos):
        update_volume(module, array)
    elif state == 'present' and volume and module.params['move']:
        move_volume(module, array)
    elif state == 'present' and volume and module.params['rename']:
        rename_volume(module, array)
    elif state == 'present' and destroyed and not module.params['move'] and not module.params['rename']:
        recover_volume(module, array)
    elif state == 'present' and destroyed and module.params['move']:
        module.fail_json(msg='Volume {0} exists, but in destroyed state'.format(module.params['name']))
    elif state == 'present' and volume and target:
        copy_from_volume(module, array)
    elif state == 'present' and volume and not target:
        copy_from_volume(module, array)
    elif state == 'absent' and volume:
        delete_volume(module, array)
    elif state == 'absent' and destroyed:
        eradicate_volume(module, array)
    elif state == 'present' and not volume or not size:
        module.fail_json(msg="Size must be specified to create a new volume")
    elif state == 'absent' and not volume:
        module.exit_json(changed=False)

    module.exit_json(changed=False)


if __name__ == '__main__':
    main()
