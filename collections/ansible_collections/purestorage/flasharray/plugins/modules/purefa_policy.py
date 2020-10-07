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
module: purefa_policy
version_added: '1.5.0'
short_description: Manage FlashArray File System Policies
description:
- Manage FlashArray file system policies for NFS, SMB and snapshot
author:
- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
options:
  name:
    description:
    - Name of the policy
    type: str
    required: true
  state:
    description:
    - Define whether the policy should exist or not.
    default: present
    choices: [ absent, present ]
    type: str
  policy:
    description:
    - The type of policy to use
    choices: [ nfs, smb, snapshot ]
    required: true
    type: str
  enabled:
    description:
    - Define if policy is enabled or not
    type: bool
    default: true
  smb_anon_allowed:
    description:
    - Specifies whether access to information is allowed for anonymous users
    type: bool
    default: false
  client:
    description:
    - Specifies which SMB or NFS clients are given access
    - Accepted notation, IP, IP mask, or hostname
    type: str
  smb_encrypt:
    description:
    - Specifies whether the remote client is required to use SMB encryption
    type: bool
    default: False
  nfs_access:
    description:
    - Specifies access control for the export
    choices: [ root-squash, no-root-squash ]
    type: str
    default: root-squash
  nfs_permission:
    description:
    - Specifies which read-write client access permissions are allowed for the export
    choices: [ ro, rw ]
    default: rw
    type: str
  snap_at:
    description:
    - Specifies the number of hours since midnight at which to take a snapshot
      or the hour including AM/PM
    - Can only be set on the rule with the smallest I(snap_every) value.
    - Cannot be set if the I(snap_every) value is not measured in days.
    - Can only be set for at most one rule in the same policy.
    type: str
  snap_every:
    description:
    - Specifies the interval between snapshots, in minutes.
    - The value for all rules must be multiples of one another.
    - Must be unique for each rule in the same policy.
    - Value must be between 5 and 525600.
    type: int
  snap_keep_for:
    description:
    - Specifies the period that snapshots are retained before they are eradicated, in minutes.
    - Cannot be less than the I(snap_every) value of the rule.
    - Value must be unique for each rule in the same policy.
    - Value must be between 5 and 525600.
    type: int
  snap_client_name:
    description:
    - The customizable portion of the client visible snapshot name.
    type: str
  rename:
    description:
    - New name of policy
    type: str
extends_documentation_fragment:
- purestorage.flasharray.purestorage.fa
'''

EXAMPLES = r'''
- name: Create an NFS policy with no rules
  purefa_policy:
    name: export1
    policy: nfs
    nfs_access: no-root-squash
    nfs_permission: ro
    client: client1
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Create an NFS policy with initial rule
  purefa_policy:
    name: export1
    policy: nfs
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Disable a policy
  purefa_policy:
    name: export1
    enabled: false
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Add rule to existing NFS export policy
  purefa_policy:
    name: export1
    policy: nfs
    nfs_access: no-root-squash
    nfs_permission: ro
    client: client2
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Add rule to existing SMB export policy
  purefa_policy:
    name: export1
    policy: nfs
    smb_encrypt: yes
    smb_anon_allowed: no
    client: client1
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Delete policy rule for a client
  purefa_policy:
    name: export1
    policy: nfs
    client: client2
    state: absent
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Delete policy
  purefa_policy:
    name: export1
    policy: nfs
    state: absent
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
'''

RETURN = r'''
'''

HAS_PURESTORAGE = True
try:
    from pypureclient import flasharray
except ImportError:
    HAS_PURESTORAGE = False

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.flasharray.plugins.module_utils.purefa import get_system, get_array, purefa_argument_spec

MIN_REQUIRED_API_VERSION = '2.3'


def _convert_to_millisecs(hour):
    if hour[-2:].upper() == "AM" and hour[:2] == "12":
        return 0
    elif hour[-2:].upper() == "AM":
        return int(hour[:-2]) * 3600000
    elif hour[-2:].upper() == "PM" and hour[:2] == "12":
        return 43200000
    return (int(hour[:-2]) + 12) * 3600000


def rename_policy(module, array):
    """Rename a file system policy"""
    changed = True
    if not module.check_mode:
        changed = False
        target_exists = bool(array.get_policies(names=[module.params['rename']]).status_code == 200)
        if target_exists:
            module.fail_json(msg="Rename failed - Target policy {0} already exists".format(module.params['rename']))
        else:
            if module.params['policy'] == 'nfs':
                res = array.patch_policies_nfs(names=[module.params['name']],
                                               policy=flasharray.PolicyPatch(name=module.params['rename']))
                if res.status_code == 200:
                    changed = True
                else:
                    module.fail_json(msg="Failed to rename NFS policy {0} to {1}".format(module.params['name'], module.params['rename']))
            elif module.params['policy'] == 'smb':
                res = array.patch_policies_smb(names=[module.params['name']],
                                               policy=flasharray.PolicyPatch(name=module.params['rename']))
                if res.status_code == 200:
                    changed = True
                else:
                    module.fail_json(msg="Failed to rename SMB policy {0} to {1}".format(module.params['name'], module.params['rename']))
            else:
                res = array.patch_policies_snapshot(names=[module.params['name']],
                                                    policy=flasharray.PolicyPatch(name=module.params['rename']))
                if res.status_code == 200:
                    changed = True
                else:
                    module.fail_json(msg="Failed to rename snapshot policy {0} to {1}".format(module.params['name'], module.params['rename']))
    module.exit_json(changed=changed)


def delete_policy(module, array):
    """Delete a file system policy or rule within a policy"""
    changed = True
    if not module.check_mode:
        changed = False
        if module.params['policy'] == 'nfs':
            if not module.params['client']:
                res = array.delete_policies_nfs(names=[module.params['name']])
                if res.status_code == 200:
                    changed = True
                else:
                    module.fail_json(msg="Deletion of NFS policy {0} failed. Error: {1}".format(module.params['name'], res.errors[0].message))
            else:
                rules = list(array.get_policies_nfs_client_rules(policy_names=[module.params['name']]).items)
                if rules:
                    rule_name = ''
                    for rule in range(0, len(rules)):
                        if rules[rule].client == module.params['client']:
                            rule_name = rules[rule].name
                            break
                    if rule_name:
                        deleted = bool(array.delete_policies_nfs_client_rules(policy_names=[module.params['name']], names=[rule_name]).status_code == 200)
                        if deleted:
                            changed = True
                        else:
                            module.fail_json(msg="Failed to delete client {0} from NFS policy {1}. Error: {2}".format(module.params['client'],
                                                                                                                      module.params['name'],
                                                                                                                      deleted.errors[0].message))
        elif module.params['policy'] == 'smb':
            if not module.params['client']:
                res = array.delete_policies_smb(names=[module.params['name']])
                if res.status_code == 200:
                    changed = True
                else:
                    module.fail_json(msg="Deletion of SMB policy {0} failed. Error: {1}".format(module.params['name'], res.errors[0].message))
            else:
                rules = list(array.get_policies_smb_client_rules(policy_names=[module.params['name']]).items)
                if rules:
                    rule_name = ''
                    for rule in range(0, len(rules)):
                        if rules[rule].client == module.params['client']:
                            rule_name = rules[rule].name
                            break
                    if rule_name:
                        deleted = bool(array.delete_policies_smb_client_rules(policy_names=[module.params['name']], names=[rule_name]).status_code == 200)
                        if deleted:
                            changed = True
                        else:
                            module.fail_json(msg="Failed to delete client {0} from SMB policy {1}. Error: {2}".format(module.params['client'],
                                                                                                                      module.params['name'],
                                                                                                                      deleted.errors[0].message))
        else:
            if not module.params['snap_client_name']:
                res = array.delete_policies_snapshot(names=[module.params['name']])
                if res.status_code == 200:
                    changed = True
                else:
                    module.fail_json(msg="Deletion of Snapshot policy {0} failed. Error: {1}".format(module.params['name'], res.errors[0].message))
            else:
                rules = list(array.get_policies_snapshot_rules(policy_names=[module.params['name']]).items)
                if rules:
                    rule_name = ''
                    for rule in range(0, len(rules)):
                        if rules[rule].client_name == module.params['snap_client_name']:
                            rule_name = rules[rule].name
                            break
                    if rule_name:
                        deleted = bool(array.delete_policies_snapshot_rules(policy_names=[module.params['name']], names=[rule_name]).status_code == 200)
                        if deleted:
                            changed = True
                        else:
                            module.fail_json(msg="Failed to delete client {0} from Snapshot policy {1}. Error: {2}".format(module.params['snap_client_name'],
                                                                                                                           module.params['name'],
                                                                                                                           deleted.errors[0].message))

    module.exit_json(changed=changed)


def create_policy(module, array):
    """Create a file system export"""
    changed = True
    if not module.check_mode:
        changed = False
        if module.params['policy'] == 'nfs':
            created = array.post_policies_nfs(names=[module.params['name']], policy=flasharray.PolicyPost(enabled=module.params['enabled']))
            if created.status_code == 200:
                if module.params['client']:
                    rules = flasharray.PolicyrulenfsclientpostRules(access=module.params['nfs_access'],
                                                                    client=module.params['client'],
                                                                    permission=module.params['nfs_permission'])
                    rule = flasharray.PolicyRuleNfsClientPost(rules=[rules])
                    rule_created = array.post_policies_nfs_client_rules(policy_names=[module.params['name']], rules=rule)
                    if rule_created.status_code != 200:
                        module.fail_json(msg="Failed to create rule for NFS policy {0}. Error: {1}".format(module.params['name'],
                                                                                                           rule_created.errors[0].message))
                changed = True
            else:
                module.params(msg="Failed to create NFS policy {0}. Error: {1}".format(module.params['name'], created.errors[0].message))
        elif module.params['policy'] == 'smb':
            created = array.post_policies_smb(names=[module.params['name']], policy=flasharray.PolicyPost(enabled=module.params['enabled']))
            if created.status_code == 200:
                changed = True
                if module.params['client']:
                    rules = flasharray.PolicyrulesmbclientpostRules(anonymous_access_allowed=module.params['smb_anon_allowed'],
                                                                    client=module.params['client'],
                                                                    smb_encryption_required=module.params['smb_encrypt'])
                    rule = flasharray.PolicyRuleSmbClientPost(rules=[rules])
                    rule_created = array.post_policies_smb_client_rules(policy_names=[module.params['name']], rules=rule)
                    if rule_created.status_code != 200:
                        module.fail_json(msg="Failed to create rule for SMB policy {0}. Error: {1}".format(module.params['name'],
                                                                                                           rule_created.errors[0].message))
            else:
                module.params(msg="Failed to create SMB policy {0}. Error: {1}".format(module.params['name'], created.errors[0].message))
        else:
            created = array.post_policies_snapshot(names=[module.params['name']], policy=flasharray.PolicyPost(enabled=module.params['enabled']))
            if created.status_code == 200:
                changed = True
                if module.params['snap_client_name']:
                    if module.params['snap_keep_for'] < module.params['snap_every']:
                        module.fail_json(msg='Retention period (snap_keep_for) cannot be less than snapshot interval (snap_every).')
                    if module.params['snap_at']:
                        if not module.params['snap_every'] % 1440 == 0:
                            module.fail_json(msg='snap_at time can only be set if snap_every is multiple of 1440')
                        rules = flasharray.PolicyrulesnapshotpostRules(at=_convert_to_millisecs(module.params['snap_at']),
                                                                       client_name=module.params['snap_client_name'],
                                                                       every=module.params['snap_every'] * 60000,
                                                                       keep_for=module.params['snap_keep_for'] * 60000)
                    else:
                        rules = flasharray.PolicyrulesnapshotpostRules(client_name=module.params['snap_client_name'],
                                                                       every=module.params['snap_every'] * 60000,
                                                                       keep_for=module.params['snap_keep_for'] * 60000)
                    rule = flasharray.PolicyRuleSnapshotPost(rules=[rules])
                    rule_created = array.post_policies_snapshot_rules(policy_names=[module.params['name']], rules=rule)
                    if rule_created.status_code != 200:
                        module.fail_json(msg="Failed to create rule for Snapshot policy {0}. Error: {1}".format(module.params['name'],
                                                                                                                rule_created.errors[0].message))
            else:
                module.params(msg="Failed to create Snapshot policy {0}. Error: {1}".format(module.params['name'], created.errors[0].message))
    module.exit_json(changed=changed)


def update_policy(module, array):
    """ Update an existing policy including add/remove rules"""
    changed = True
    if not module.check_mode:
        changed = changed_rule = changed_enable = False
        if module.params['policy'] == 'nfs':
            try:
                current_enabled = list(array.get_policies_nfs(names=[module.params['name']]).items)[0].enabled
            except Exception:
                module.fail_json(msg='Incorrect policy type specified for existing policy {0}'.format(module.params['name']))
            if current_enabled != module.params['enabled']:
                res = array.patch_policies_nfs(names=[module.params['name']], policy=flasharray.PolicyPatch(enabled=module.params['enabled']))
                if res.status_code != 200:
                    module.exit_json(msg="Failed to enable/disable NFS policy {0}".format(module.params['name']))
                else:
                    changed_enable = True
            if module.params['client']:
                rules = list(array.get_policies_nfs_client_rules(policy_names=[module.params['name']]).items)
                if rules:
                    rule_name = ''
                    for rule in range(0, len(rules)):
                        if rules[rule].client == module.params['client']:
                            rule_name = rules[rule].name
                            break
                    if not rule_name:
                        rules = flasharray.PolicyrulesmbclientpostRules(anonymous_access_allowed=module.params['smb_anon_allowed'],
                                                                        client=module.params['client'],
                                                                        smb_encryption_required=module.params['smb_encrypt'])
                        rule = flasharray.PolicyRuleNfsClientPost(rules=[rules])
                        rule_created = array.post_policies_nfs_client_rules(policy_names=[module.params['name']], rules=rule)
                        if rule_created.status_code != 200:
                            module.fail_json(msg="Failed to create new rule for NFS policy {0}. Error: {1}".format(module.params['name'],
                                                                                                                   rule_created.errors[0].message))
                        else:
                            changed_rule = True
                else:
                    rules = flasharray.PolicyrulesmbclientpostRules(anonymous_access_allowed=module.params['smb_anon_allowed'],
                                                                    client=module.params['client'],
                                                                    smb_encryption_required=module.params['smb_encrypt'])
                    rule = flasharray.PolicyRuleNfsClientPost(rules=[rules])
                    rule_created = array.post_policies_nfs_client_rules(policy_names=[module.params['name']], rules=rule)
                    if rule_created.status_code != 200:
                        module.fail_json(msg="Failed to create new rule for SMB policy {0}. Error: {1}".format(module.params['name'],
                                                                                                               rule_created.errors[0].message))
                    else:
                        changed_rule = True
        elif module.params['policy'] == 'smb':
            try:
                current_enabled = list(array.get_policies_smb(names=[module.params['name']]).items)[0].enabled
            except Exception:
                module.fail_json(msg='Incorrect policy type specified for existing policy {0}'.format(module.params['name']))
            if current_enabled != module.params['enabled']:
                res = array.patch_policies_smb(names=[module.params['name']], policy=flasharray.PolicyPatch(enabled=module.params['enabled']))
                if res.status_code != 200:
                    module.exit_json(msg="Failed to enable/disable SMB policy {0}".format(module.params['name']))
                else:
                    changed_enable = True
            if module.params['client']:
                rules = list(array.get_policies_smb_client_rules(policy_names=[module.params['name']]).items)
                if rules:
                    rule_name = ''
                    for rule in range(0, len(rules)):
                        if rules[rule].client == module.params['client']:
                            rule_name = rules[rule].name
                            break
                    if not rule_name:
                        rules = flasharray.PolicyrulesmbclientpostRules(access=module.params['nfs_access'],
                                                                        client=module.params['client'],
                                                                        permission=module.params['nfs_permission'])
                        rule = flasharray.PolicyRuleSmbClientPost(rules=[rules])
                        rule_created = array.post_policies_smb_client_rules(policy_names=[module.params['name']], rules=rule)
                        if rule_created.status_code != 200:
                            module.fail_json(msg="Failed to create new rule for SMB policy {0}. Error: {1}".format(module.params['name'],
                                                                                                                   rule_created.errors[0].message))
                        else:
                            changed_rule = True
                else:
                    rules = flasharray.PolicyrulesmbclientpostRules(access=module.params['nfs_access'],
                                                                    client=module.params['client'],
                                                                    permission=module.params['nfs_permission'])
                    rule = flasharray.PolicyRuleSmbClientPost(rules=[rules])
                    rule_created = array.post_policies_smb_client_rules(policy_names=[module.params['name']], rules=rule)
                    if rule_created.status_code != 200:
                        module.fail_json(msg="Failed to create new rule for SMB policy {0}. Error: {1}".format(module.params['name'],
                                                                                                               rule_created.errors[0].message))
                    else:
                        changed_rule = True
        else:
            try:
                current_enabled = list(array.get_policies_snapshot(names=[module.params['name']]).items)[0].enabled
            except Exception:
                module.fail_json(msg='Incorrect policy type specified for existing policy {0}'.format(module.params['name']))
            if current_enabled != module.params['enabled']:
                res = array.patch_policies_snapshot(names=[module.params['name']], policy=flasharray.PolicyPost(enabled=module.params['enabled']))
                if res.status_code != 200:
                    module.exit_json(msg="Failed to enable/disable snapshot policy {0}".format(module.params['name']))
                else:
                    changed_enable = True
            if module.params['snap_client_name']:
                if module.params['snap_at']:
                    if not module.params['snap_every'] % 1440 == 0:
                        module.fail_json(msg='snap_at time can only be set if snap_every is multiple of 1440')
                if module.params['snap_keep_for'] < module.params['snap_every']:
                    module.fail_json(msg='Retention period (snap_keep_for) cannot be less than snapshot interval (snap_every).')
                rules = list(array.get_policies_snapshot_rules(policy_names=[module.params['name']]).items)
                if rules:
                    rule_name = ''
                    for rule in range(0, len(rules)):
                        if rules[rule].client_name == module.params['snap_client_name']:
                            rule_name = rules[rule].name
                            break
                    if not rule_name:
                        if module.params['snap_keep_for'] < module.params['snap_every']:
                            module.fail_json(msg='Retention period (snap_keep_for) cannot be less than snapshot interval (snap_every).')
                        if module.params['snap_at']:
                            if not module.params['snap_every'] % 1440 == 0:
                                module.fail_json(msg='snap_at time can only be set if snap_every is multiple of 1440')
                            rules = flasharray.PolicyrulesnapshotpostRules(at=_convert_to_millisecs(module.params['snap_at']),
                                                                           client_name=module.params['snap_client_name'],
                                                                           every=module.params['snap_every'] * 60000,
                                                                           keep_for=module.params['snap_keep_for'] * 60000)
                        else:
                            rules = flasharray.PolicyrulesnapshotpostRules(client_name=module.params['snap_client_name'],
                                                                           every=module.params['snap_every'] * 60000,
                                                                           keep_for=module.params['snap_keep_for'] * 60000)
                        rule = flasharray.PolicyRuleSnapshotPost(rules=[rules])
                        rule_created = array.post_policies_snapshot_rules(policy_names=[module.params['name']], rules=rule)
                        if rule_created.status_code != 200:
                            err_no = len(rule_created.errors) - 1
                            module.fail_json(msg="Failed to create new rule for Snapshot policy {0}. Error: {1}".format(module.params['name'],
                                                                                                                        rule_created.errors[err_no].message))
                        else:
                            changed_rule = True
                else:
                    if module.params['snap_keep_for'] < module.params['snap_every']:
                        module.fail_json(msg='Retention period (snap_keep_for) cannot be less than snapshot interval (snap_every).')
                    if module.params['snap_at']:
                        if not module.params['snap_every'] % 1440 == 0:
                            module.fail_json(msg='snap_at time can only be set if snap_every is multiple of 1440')
                        rules = flasharray.PolicyrulesnapshotpostRules(at=_convert_to_millisecs(module.params['snap_at']),
                                                                       client_name=module.params['snap_client_name'],
                                                                       every=module.params['snap_every'] * 60000,
                                                                       keep_for=module.params['snap_keep_for'] * 60000)
                    else:
                        rules = flasharray.PolicyrulesnapshotpostRules(client_name=module.params['snap_client_name'],
                                                                       every=module.params['snap_every'] * 60000,
                                                                       keep_for=module.params['snap_keep_for'] * 60000)
                    rule = flasharray.PolicyRuleSnapshotPost(rules=[rules])
                    rule_created = array.post_policies_snapshot_rules(policy_names=[module.params['name']], rules=rule)
                    if rule_created.status_code != 200:
                        err_no = len(rule_created.errors) - 1
                        module.fail_json(msg="Failed to create new rule for Snapshot policy {0}. Error: {1}".format(module.params['name'],
                                                                                                                    rule_created.errors[err_no].message))
                    else:
                        changed_rule = True
        if changed_rule or changed_enable:
            changed = True
    module.exit_json(changed=changed)


def main():
    argument_spec = purefa_argument_spec()
    argument_spec.update(dict(
        state=dict(type='str', default='present', choices=['absent', 'present']),
        nfs_access=dict(type='str', default='root-squash', choices=['root-squash', 'no-root-squash']),
        nfs_permission=dict(type='str', default='rw', choices=['rw', 'ro']),
        policy=dict(type='str', required=True, choices=['nfs', 'smb', 'snapshot']),
        name=dict(type='str', required=True),
        rename=dict(type='str'),
        client=dict(type='str'),
        enabled=dict(type='bool', default=True),
        snap_at=dict(type='str'),
        snap_every=dict(type='int'),
        snap_keep_for=dict(type='int'),
        snap_client_name=dict(type='str'),
        smb_anon_allowed=dict(type='bool', default=False),
        smb_encrypt=dict(type='bool', default=False),
    ))

    required_together = [['snap_keep_for', 'snap_every']]
    module = AnsibleModule(argument_spec,
                           required_together=required_together,
                           supports_check_mode=True)

    if not HAS_PURESTORAGE:
        module.fail_json(msg='py-pure-client sdk is required for this module')

    array = get_system(module)
    api_version = array._list_available_rest_versions()
    if MIN_REQUIRED_API_VERSION not in api_version:
        module.fail_json(msg='FlashArray REST version not supported. '
                             'Minimum version required: {0}'.format(MIN_REQUIRED_API_VERSION))
    array = get_array(module)
    state = module.params['state']

    exists = bool(array.get_policies(names=[module.params['name']]).status_code == 200)

    if state == 'present' and not exists:
        create_policy(module, array)
    elif state == 'present' and exists and module.params['rename']:
        rename_policy(module, array)
    elif state == 'present' and exists:
        update_policy(module, array)
    elif state == 'absent' and exists:
        delete_policy(module, array)

    module.exit_json(changed=False)


if __name__ == '__main__':
    main()
