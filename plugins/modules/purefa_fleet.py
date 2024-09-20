#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2024, Simon Dodsley (simon@purestorage.com)
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
module: purefa_fleet
version_added: '1.32.0'
short_description: Manage Fusion Fleet
description:
- Create/Modify/Delete Fusion fleet and members
author:
- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
options:
  name:
    description:
    - Name of the fleet.
    - If not provided local array will be used.
    type: str
  state:
    description:
    - Define whether to add or remove member from a fleet.
    - Create a new fleet if one does not exist.
      This will use the current array as the first member.
    default: present
    choices: [ absent, present, create ]
    type: str
  member_url:
    description:
    - Management IP address/FQDN of array to add to fleet.
    type: str
  member_api:
    description:
    - API token for target array
    type: str
extends_documentation_fragment:
- purestorage.flasharray.purestorage.fa
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

HAS_URLLIB3 = True
try:
    import urllib3
except ImportError:
    HAS_URLLIB3 = False

HAS_DISTRO = True
try:
    import distro
except ImportError:
    HAS_DISTRO = False

HAS_PURESTORAGE = True
try:
    from pypureclient import flasharray
    from pypureclient.flasharray import (
        FleetMemberPost,
        FleetmemberpostMember,
        FleetmemberspostMembers,
    )
except ImportError:
    HAS_PURESTORAGE = False

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.flasharray.plugins.module_utils.purefa import (
    get_array,
    purefa_argument_spec,
)
from ansible_collections.purestorage.flasharray.plugins.module_utils.version import (
    LooseVersion,
)

VERSION = 1.5
USER_AGENT_BASE = "Ansible"
MIN_REQUIRED_API_VERSION = "2.36"


def create_fleet(module, array, fleet):
    """Create new fleet - only ever called once per fleet"""
    changed = False
    if not fleet:
        changed = True
        if not module.check_mode:
            res = array.post_fleets(names=[module.params["name"]])
            if res.status_code != 200:
                module.fail_json(
                    msg="Failed to create fleet {0}. Error: {1}".format(
                        module.params["name"], res.errors[0].message
                    )
                )
    module.exit_json(changed=changed)


def add_fleet_members(module, array, fleet):
    """Add new members to the fleet"""
    changed = False
    part_failure = False
    try:
        fleet_key = list(array.post_fleets_fleet_key().items)[0].fleet_key
    except Exception:
        module.fail_json(msg="Fleet key generation failed")
    for member in module.params["member"]:
        if HAS_URLLIB3 and module.params["disable_warnings"]:
            urllib3.disable_warnings()
        if HAS_DISTRO:
            user_agent = "%(base)s %(class)s/%(version)s (%(platform)s)" % {
                "base": USER_AGENT_BASE,
                "class": __name__,
                "version": VERSION,
                "platform": distro.name(pretty=True),
            }
        else:
            user_agent = "%(base)s %(class)s/%(version)s (%(platform)s)" % {
                "base": USER_AGENT_BASE,
                "class": __name__,
                "version": VERSION,
                "platform": platform.platform(),
            }
        changed = True
        if not module.check_mode:
            remote_system = flasharray.Client(
                target=module.params["member"][mmeber]["mmeber_url"],
                api_token=module.params["member"][member]["member_api"],
                user_agent=user_agent,
            )
            local_name = list(remote_system.get_arrays().items)[0].name
            res = remote_system.post_fleets_members(
                fleet_names=module.params["fleet"],
                members=FleetMemberPost(
                    members=FleetmemberspostMembers(
                        key=fleet_key, member=FleetmemberpostMember(name=local_name)
                    )
                ),
            )
            if res.status_code != 200:
                module.warn(
                    "Array {0} failed to join fleet {1}. Error: {2}".format(
                        local_name, module.params["fleet"], res.errors[0].message
                    )
                )
                part_failure = True
    if part_failure:
        module.fail_json(
            msg="At least one member failed to join the fleet. See previous messages"
        )
    module.exit_json(changed=changed)


def delete_fleet_members(module, array, fleet):
    """Create new fleet - only ever called once"""
    changed = False
    if module.params["member"]:
        # Remove member from fleet
        changed = True
    else:
        # Delete the entire fleet
        changed = True
    module.exit_json(changed=changed)


def main():
    argument_spec = purefa_argument_spec()
    argument_spec.update(
        dict(
            name=dict(type="str"),
            state=dict(
                type="str", default="present", choices=["absent", "present", "create"]
            ),
            member_url=dict(type="str"),
            member_api=dict(type="str"),
        )
    )

    required_if = ["state", "present", ["member_url", "member_api"]]

    module = AnsibleModule(
        argument_spec, required_if=required_if, supports_check_mode=True
    )

    if not HAS_PURESTORAGE:
        module.fail_json(msg="py-pure-client sdk is required for this module")

    array = get_array(module)
    api_version = array.get_rest_version()
    if LooseVersion(MIN_REQUIRED_API_VERSION) > LooseVersion(api_version):
        module.fail_json(
            msg="FlashArray REST version not supported. "
            "Minimum version required: {0}".format(MIN_REQUIRED_API_VERSION)
        )
    state = module.params["state"]

    fleet_res = array.get_fleets()
    if fleet_res.status_code == 404:
        module.fail_json(
            msg="Fusion is not enabled on this system. "
            "Please speak to Pure Support to enable this feature"
        )
    else:
        fleet = list(fleet_res.items)

    if state == "create":
        create_fleet(module, array, fleet)
    elif state == "present" and fleet:
        add_fleet_members(modue, array, fleet)
    elif state == "absent" and fleet:
        delete_fleet_members(modue, array, fleet)
    else:
        module.exit_json(changed=False)


if __name__ == "__main__":
    main()
