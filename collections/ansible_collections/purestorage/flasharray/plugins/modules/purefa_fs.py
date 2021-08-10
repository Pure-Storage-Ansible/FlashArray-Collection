#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020, Simon Dodsley (simon@purestorage.com)
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
module: purefa_fs
version_added: '1.5.0'
short_description: Manage FlashArray File Systems
description:
- Create/Delete FlashArray File Systems
author:
- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
options:
  name:
    description:
    - Name of the file system
    type: str
    required: true
  state:
    description:
    - Define whether the file system should exist or not.
    default: present
    choices: [ absent, present ]
    type: str
  eradicate:
    description:
    - Define whether to eradicate the file system on delete or leave in trash.
    type: bool
    default: false
  rename:
    description:
    - Value to rename the specified file system to
    type: str
extends_documentation_fragment:
- purestorage.flasharray.purestorage.fa
"""

EXAMPLES = r"""
- name: Create file system foo
  purefa_fs:
    name: foo
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Delete and eradicate file system foo
  purefa_fs:
    name: foo
    eradicate: true
    state: absent
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Rename file system foo to bar
  purefa_fs:
    name: foo
    rename: bar
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
"""

RETURN = r"""
"""

HAS_PURESTORAGE = True
try:
    from pypureclient import flasharray
except ImportError:
    HAS_PURESTORAGE = False

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.flasharray.plugins.module_utils.purefa import (
    get_system,
    get_array,
    purefa_argument_spec,
)

MIN_REQUIRED_API_VERSION = "2.2"


def delete_fs(module, array):
    """Delete a file system"""
    changed = True
    if not module.check_mode:
        try:
            file_system = flasharray.FileSystemPatch(destroyed=True)
            array.patch_file_systems(
                names=[module.params["name"]], file_system=file_system
            )
        except Exception:
            module.fail_json(
                msg="Failed to delete file system {0}".format(module.params["name"])
            )
        if module.params["eradicate"]:
            try:
                array.delete_file_systems(names=[module.params["name"]])
            except Exception:
                module.fail_json(
                    msg="Eradication of file system {0} failed".format(
                        module.params["name"]
                    )
                )
    module.exit_json(changed=changed)


def recover_fs(module, array):
    """Recover a deleted file system"""
    changed = True
    if not module.check_mode:
        try:
            file_system = flasharray.FileSystemPatch(destroyed=False)
            array.patch_file_systems(
                names=[module.params["name"]], file_system=file_system
            )
        except Exception:
            module.fail_json(
                msg="Failed to recover file system {0}".format(module.params["name"])
            )
    module.exit_json(changed=changed)


def eradicate_fs(module, array):
    """Eradicate a file system"""
    changed = True
    if not module.check_mode:
        try:
            array.delete_file_systems(names=[module.params["name"]])
        except Exception:
            module.fail_json(
                msg="Failed to eradicate file system {0}".format(module.params["name"])
            )
    module.exit_json(changed=changed)


def rename_fs(module, array):
    """Rename a file system"""
    changed = False
    try:
        target = list(array.get_file_systems(names=[module.params["rename"]]).items)[0]
    except Exception:
        target = None
    if not target:
        changed = True
        if not module.check_mode:
            try:
                file_system = flasharray.FileSystemPatch(name=module.params["rename"])
                array.patch_file_systems(
                    names=[module.params["name"]], file_system=file_system
                )
            except Exception:
                module.fail_json(
                    msg="Failed to rename file system {0}".format(module.params["name"])
                )
    else:
        module.fail_json(
            msg="Target file system {0} already exists".format(module.params["rename"])
        )
    module.exit_json(changed=changed)


def create_fs(module, array):
    """Create a file system"""
    changed = True
    if not module.check_mode:
        try:
            array.post_file_systems(names=[module.params["name"]])
        except Exception:
            module.fail_json(
                msg="Failed to create file system {0}".format(module.params["name"])
            )
    module.exit_json(changed=changed)


def main():
    argument_spec = purefa_argument_spec()
    argument_spec.update(
        dict(
            state=dict(type="str", default="present", choices=["absent", "present"]),
            eradicate=dict(type="bool", default=False),
            name=dict(type="str", required=True),
            rename=dict(type="str"),
        )
    )

    module = AnsibleModule(argument_spec, supports_check_mode=True)

    if not HAS_PURESTORAGE:
        module.fail_json(msg="py-pure-client sdk is required for this module")

    array = get_system(module)
    api_version = array._list_available_rest_versions()

    if MIN_REQUIRED_API_VERSION not in api_version:
        module.fail_json(
            msg="FlashArray REST version not supported. "
            "Minimum version required: {0}".format(MIN_REQUIRED_API_VERSION)
        )
    array = get_array(module)
    state = module.params["state"]

    try:
        filesystem = list(array.get_file_systems(names=[module.params["name"]]).items)[
            0
        ]
        exists = True
    except Exception:
        exists = False

    if state == "present" and not exists:
        create_fs(module, array)
    elif (
        state == "present"
        and exists
        and module.params["rename"]
        and not filesystem.destroyed
    ):
        rename_fs(module, array)
    elif (
        state == "present"
        and exists
        and filesystem.destroyed
        and not module.params["rename"]
    ):
        recover_fs(module, array)
    elif state == "absent" and exists and not filesystem.destroyed:
        delete_fs(module, array)
    elif (
        state == "absent"
        and exists
        and module.params["eradicate"]
        and filesystem.destroyed
    ):
        eradicate_fs(module, array)

    module.exit_json(changed=False)


if __name__ == "__main__":
    main()
