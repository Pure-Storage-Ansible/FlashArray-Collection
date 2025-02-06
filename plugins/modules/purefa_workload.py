#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2025, Simon Dodsley (simon@purestorage.com)
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
module: purefa_workload
version_added: '1.33.0'
short_description: Manage Fusion Fleet Workloads
description:
- Apply/Rename/Delete Fusion fleet workloads
author:
- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
options:
  name:
    description:
    - Name of the workload.
    type: str
    required: true
  state:
    description:
    - Define whether to create, rename or delete a fleet workload.
    default: present
    choices: [ absent, present, rename ]
    type: str
  preset:
    description:
    - name of existing preset to use as the basis of the workload
    type: str
  rename:
    description:
    - new name for workload
    type: str
  eradicate:
    description:
    - whether to eradicate a workload
    type: bool
    default: false
  placement:
    description:
    - name of target on which the workload will be deployed
    type: str
  recommendation:
    description:
    - whether to use the Fusion placement recommendation based
      on the workload preset definitions.
    - This will use the first recommended placement if more than
      one is available
    default: false
    type: bool
extends_documentation_fragment:
- purestorage.flasharray.purestorage.fa
"""

EXAMPLES = r"""
- name: Create a workload using an exisitng preset on a specific placement target
  purestorage.flasharray.purefa_workload:
    name: foo
    preset: bar
    plaement: arrayB
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Create a workload using an exisitng preset using the recommended target
  purestorage.flasharray.purefa_workload:
    name: foo
    preset: bar
    recommendation: true
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Rename an existing workload
  purestorage.flasharray.purefa_workload:
    name: foo
    rename: bar
    state: rename
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Delete an existing workload
  purestorage.flasharray.purefa_workload:
    name: foo
    state: absent
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Eradicate an existing workload
  purestorage.flasharray.purefa_workload:
    name: foo
    state: absent
    eradicate: true
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Recover a deleted workload
  purestorage.flasharray.purefa_workload:
    name: foo
    state: present
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
"""

RETURN = r"""
"""

HAS_PURESTORAGE = True
try:
    from pypureclient import flasharray
    from pypureclient.flasharray import (
        FleetMemberPost,
        FleetmemberpostMember,
        FleetmemberpostMembers,
        FleetPatch,
        WorkloadPatch,
        WorkloadPost,
        WorkloadPlacementRecommendation,
    )
except ImportError:
    HAS_PURESTORAGE = False

import time
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
MIN_REQUIRED_API_VERSION = "2.40"


def create_workload(module, array, fleet, preset_config):
    """Create fleet workload using existing preset"""
    changed = True
    parameters = preset_config.parameters
    repl_config = preset_config.periodic_replication_configurations
    placement_config = preset_config.placement_configurations
    qos_config = preset_config.qos_configurations
    snap_config = preset_config.snapshot_configurations
    vol_config = preset_config.volume_configurations
    tags = preset_config.workload_tags
    if module.params["recommendation"]:
        # Start the workload calculation for the preset being used
        res = array.post_workloads_placement_recommendations(
            inputs=WorkloadPlacementRecommendation(),
            preset_names=[fleet + ":" + module.params["preset"]],
        )
        if res.status_code != 200:
            module.fail_json(
                msg="Recommendation calculation failure. Error: {0}".format(
                    res.errors[0].message
                )
            )
        workload_calc = list(res.items[0]).name
        # Wait for the workload calulation to complete
        result = list(
            array.get_workloads_placement_recommendations(names=[workload_calc]).items
        )[0]
        while result.status != "completed":
            time.sleep(1)
            result = list(
                array.get_workloads_placement_recommendations(
                    names=[workload_calc]
                ).items
            )[0]
        # Replace any defined placement with the result from the recommendation
        module.params["placement"] = result.results[0].placements[0].targets[0].name
    if not module.check_mode:
        res = array.post_workloads(
            names=[module.params["name"]], workload=WorkloadPost()
        )
        if res.status_code != 200:
            module.fail_json(
                msg="Failed to create fleet {0}. Error: {1}".format(
                    module.params["name"], res.errors[0].message
                )
            )
    module.exit_json(changed=changed)


def delete_workload(module, array):
    """Delete the workload"""
    changed = True
    if not module.check_mode:
        res = array.patch_workloads(
            names=[module.params["name"]],
            workload=WorkloadPatch(destroyed=True),
        )
        if res.status_code != 200:
            module.fail_json(
                msg="Workload deletion failed. Error: {0}".format(res.errors[0].message)
            )
        if module.params["eradicate"]:
            eradicate_workload(module, array)
    module.exit_json(changed=changed)


def eradicate_workload(module, array):
    """Eradicate the workload"""
    changed = True
    if not module.check_mode:
        res = array.delete_workloads(
            names=[module.params["name"]],
        )
        if res.status_code != 200:
            module.fail_json(
                msg="Workload eradication failed. Error: {0}".format(
                    res.errors[0].message
                )
            )
    module.exit_json(changed=changed)


def recover_workload(module, array):
    """Recover the workload"""
    changed = True
    if not module.check_mode:
        res = array.patch_workloads(
            names=[module.params["name"]],
            workload=WorkloadPatch(destroyed=False),
        )
        if res.status_code != 200:
            module.fail_json(
                msg="Workload recovery failed. Error: {0}".format(res.errors[0].message)
            )
    module.exit_json(changed=changed)


def rename_workload(module, array):
    """Rename the workload"""
    changed = True
    if not module.check_mode:
        res = array.patch_workloads(
            names=[module.params["name"]],
            workload=WorkloadPatch(name=module.params["rename"]),
        )
        if res.status_code != 200:
            module.fail_json(
                msg="Workload rename failed. Error: {0}".format(res.errors[0].message)
            )
    module.exit_json(changed=changed)


def main():
    argument_spec = purefa_argument_spec()
    argument_spec.update(
        dict(
            name=dict(type="str", required=True),
            state=dict(
                type="str", default="present", choices=["absent", "present", "rename"]
            ),
            preset=dict(type="str"),
            rename=dict(type="str"),
            eradicate=dict(type="bool", default=False),
            plaement=dict(type="str"),
            recommendation=dict(type="bool", default=False),
        )
    )

    module = AnsibleModule(argument_spec, supports_check_mode=True)

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
    if fleet_res.status_code != 200:
        module.fail_json(
            msg="Fusion is not enabled on this system "
            "or the array is not a member of a fleet."
        )
    fleet = list(fleet_res.items)[0].name

    workload_destroyed = False
    workload_exists = False
    preset_config = []
    res = array.get_workloads(names=[module.params["name"]])
    if res.status_code == 200:
        workload_exists = True
        workload_destroyed = list(res.items)[0].destroyed

    if state == "present" and not workload_destroyed and not workload_exists:
        res = array.get_presets_workload(
            names=[module.params["preset"]], context_names=[fleet]
        )
        if res.status_code != 200:
            module.fail_json(
                msg="Preset {0} does not exist in fleet {1}".format(
                    module.params["preset"], fleet
                )
            )
        preset_config = list(res.items)[0]
    if (
        state == "present"
        and workload_exists
        and module.params["rename"]
        and not workload_deleted
    ):
        rename_workload(module, array)
    elif state == "present" and not workload_exists:
        create_workload(module, array, fleet, preset_config)
    elif state == "present" and workload_exists and workload_destroyed:
        recover_workload(module, array)
    elif state == "absent" and workload_exists and not workload_destroyed:
        delete_workload(module, array)
    elif state == "absent" and workload_destroyed and module.params["eradicate"]:
        eradicate_workload(module, array)
    else:
        module.exit_json(changed=False)


if __name__ == "__main__":
    main()
