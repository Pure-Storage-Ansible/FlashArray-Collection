#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2021, Simon Dodsley (simon@purestorage.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: purefa_ad
version_added: '1.9.0'
short_description: Manage FlashArray Active Directory Account
description:
- Add or delete FlashArray Active Directory Account
- FlashArray allows the creation of one AD computer account, or joining of an
  existing AD computer account.
author:
- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
options:
  name:
    description:
    - Name of the AD account
    type: str
    required: true
  state:
    description:
    - Define whether the AD sccount is deleted or not
    default: present
    choices: [ absent, present ]
    type: str
  computer:
    description:
    -  The common name of the computer account to be created in the Active Directory domain.
    - If not specified, defaults to the name of the Active Directory configuration.
    type: str
  domain:
    description:
    - The Active Directory domain to join
    type: str
  username:
    description:
    - A user capable of creating a computer account within the domain
    type: str
  password:
    description:
    - Password string for I(username)
    type: str
  directory_servers:
    description:
    - A list of directory servers that will be used for lookups related to user authorization
    - Accepted server formats are IP address and DNS name
    - All specified servers must be registered to the domain appropriately in the array
      configured DNS and are only communicated with over the secure LDAP (LDAPS) protocol.
      If not specified, servers are resolved for the domain in DNS
    - The specified list can have a maximum length of 1, or 3 for Purity 6.1.6 or higher.
      If more are provided only the first allowed count used.
    type: list
    elements: str
  kerberos_servers:
    description:
    - A list of key distribution servers to use for Kerberos protocol
    - Accepted server formats are IP address and DNS name
    - All specified servers must be registered to the domain appropriately in the array
      configured DNS and are only communicated with over the secure LDAP (LDAPS) protocol.
      If not specified, servers are resolved for the domain in DNS.
    - The specified list can have a maximum length of 1, or 3 for Purity 6.1.6 or higher.
      If more are provided only the first allowed count used.
    type: list
    elements: str
  local_only:
    description:
    - Do a local-only delete of an active directory account
    type: bool
    default: false
  join_ou:
    description:
    - Distinguished name of organization unit in which the computer account
      should be created when joining the domain. e.g. OU=Arrays,OU=Storage.
    - The B(DC=...) components can be omitted.
    - If left empty, defaults to B(CN=Computers).
    - Requires Purity//FA 6.1.8 or higher
    type: str
    version_added: '1.10.0'
extends_documentation_fragment:
- purestorage.flasharray.purestorage.fa
"""

EXAMPLES = r"""
- name: Create new AD account
  purefa_ad:
    name: ad_account
    computer: FLASHARRAY
    domain: acme.com
    join_ou: "OU=Acme,OU=Dev"
    username: Administrator
    password: Password
    kerberos_servers:
    - kdc.acme.com
    directory_servers:
    - ldap.acme.com
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Delete AD account locally
  purefa_ad:
    name: ad_account
    local_only: True
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Fully delete AD account. Note that correct AD permissions are required
  purefa_ad:
    name: ad_account
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
"""

RETURN = r"""
"""

HAS_PURESTORAGE = True
try:
    from pypureclient.flasharray import ActiveDirectoryPost
except ImportError:
    HAS_PURESTORAGE = False

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.flasharray.plugins.module_utils.purefa import (
    get_system,
    get_array,
    purefa_argument_spec,
)

MIN_REQUIRED_API_VERSION = "2.2"
SERVER_API_VERSION = "2.6"
MIN_JOIN_OU_API_VERSION = "2.8"


def delete_account(module, array):
    """Delete Active directory Account"""
    changed = True
    if not module.check_mode:
        res = array.delete_active_directory(
            names=[module.params["name"]], local_only=module.params["local_only"]
        )
        if res.status_code != 200:
            module.fail_json(
                msg="Failed to delete AD Account {0}. Error: {1}".format(
                    module.params["name"], res.errors[0].message
                )
            )
    module.exit_json(changed=changed)


def create_account(module, array, api_version):
    """Create Active Directory Account"""
    changed = True
    if MIN_JOIN_OU_API_VERSION not in api_version:
        ad_config = ActiveDirectoryPost(
            computer_name=module.params["computer"],
            directory_servers=module.params["directory_servers"],
            kerberos_servers=module.params["kerberos_servers"],
            domain=module.params["domain"],
            user=module.params["username"],
            password=module.params["password"],
        )
    else:
        ad_config = ActiveDirectoryPost(
            computer_name=module.params["computer"],
            directory_servers=module.params["directory_servers"],
            kerberos_servers=module.params["kerberos_servers"],
            domain=module.params["domain"],
            user=module.params["username"],
            join_ou=module.params["join_ou"],
            password=module.params["password"],
        )
    if not module.check_mode:
        res = array.post_active_directory(
            names=[module.params["name"]],
            active_directory=ad_config,
        )
        if res.status_code != 200:
            module.fail_json(
                msg="Failed to add Active Directory Account {0}. Error: {1}".format(
                    module.params["name"], res.errors[0].message
                )
            )
    module.exit_json(changed=changed)


def main():
    argument_spec = purefa_argument_spec()
    argument_spec.update(
        dict(
            state=dict(type="str", default="present", choices=["absent", "present"]),
            username=dict(type="str"),
            password=dict(type="str", no_log=True),
            name=dict(type="str", required=True),
            computer=dict(type="str"),
            local_only=dict(type="bool", default=False),
            domain=dict(type="str"),
            join_ou=dict(type="str"),
            directory_servers=dict(type="list", elements="str"),
            kerberos_servers=dict(type="list", elements="str"),
        )
    )

    required_if = [["state", "present", ["username", "password", "domain"]]]

    module = AnsibleModule(
        argument_spec, required_if=required_if, supports_check_mode=True
    )

    if not HAS_PURESTORAGE:
        module.fail_json(msg="py-pure-client sdk is required for this module")

    array = get_system(module)
    api_version = array._list_available_rest_versions()
    if MIN_REQUIRED_API_VERSION not in api_version:
        module.fail_json(
            msg="FlashArray REST version not supported. "
            "Minimum version required: {0}".format(MIN_REQUIRED_API_VERSION)
        )
    state = module.params["state"]
    array = get_array(module)
    exists = bool(
        array.get_active_directory(names=[module.params["name"]]).status_code == 200
    )

    if not module.params["computer"]:
        module.params["computer"] = module.params["name"].replace("_", "-")
    if module.params["kerberos_servers"]:
        if SERVER_API_VERSION in api_version:
            module.params["kerberos_servers"] = module.params["kerberos_servers"][0:3]
        else:
            module.params["kerberos_servers"] = module.params["kerberos_servers"][0:1]
    if module.params["directory_servers"]:
        if SERVER_API_VERSION in api_version:
            module.params["directory_servers"] = module.params["directory_servers"][0:3]
        else:
            module.params["directory_servers"] = module.params["directory_servers"][0:1]
    if not exists and state == "present":
        create_account(module, array, api_version)
    elif exists and state == "absent":
        delete_account(module, array)

    module.exit_json(changed=False)


if __name__ == "__main__":
    main()
