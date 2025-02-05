#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2019, Simon Dodsley (simon@purestorage.com)
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
module: purefa_info
version_added: '1.0.0'
short_description: Collect information from Pure Storage FlashArray
description:
  - Collect information from a Pure Storage Flasharray running the
    Purity//FA operating system. By default, the module will collect basic
    information including hosts, host groups, protection
    groups and volume counts. Additional information can be collected
    based on the configured set of arguments.
author:
  - Pure Storage ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
options:
  gather_subset:
    description:
      - When supplied, this argument will define the information to be collected.
        Possible values for this include all, minimum, config, performance,
        capacity, network, subnet, interfaces, hgroups, pgroups, hosts,
        admins, volumes, snapshots, pods, replication, vgroups, offload, apps,
        arrays, certs, kmip, clients, policies, dir_snaps, filesystems,
        alerts, virtual_machines, subscriptions, realms and fleet.
    type: list
    elements: str
    required: false
    default: minimum
extends_documentation_fragment:
  - purestorage.flasharray.purestorage.fa
"""

EXAMPLES = r"""
- name: collect default set of information
  purestorage.flasharray.purefa_info:
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
  register: array_info
- name: show default information
  debug:
    msg: "{{ array_info['purefa_info']['default'] }}"

- name: collect configuration and capacity information
  purestorage.flasharray.purefa_info:
    gather_subset:
      - config
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
  register: array_info
- name: show configuration information
  debug:
    msg: "{{ array_info['purefa_info']['config'] }}"

- name: collect all information
  purestorage.flasharray.purefa_info:
    gather_subset:
      - all
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
- name: show all information
  debug:
    msg: "{{ array_info['purefa_info'] }}"
"""

RETURN = r"""
purefa_info:
  description: Returns the information collected from the FlashArray
  returned: always
  type: dict
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.flasharray.plugins.module_utils.purefa import (
    get_array,
    get_system,
    purefa_argument_spec,
)
from ansible_collections.purestorage.flasharray.plugins.module_utils.version import (
    LooseVersion,
)

try:
    from purestorage import purestorage
except ImportError:
    purestorage = None
from datetime import datetime
import time

SEC_TO_DAY = 86400000
ADMIN_API_VERSION = "1.14"
S3_REQUIRED_API_VERSION = "1.16"
LATENCY_REQUIRED_API_VERSION = "1.16"
AC_REQUIRED_API_VERSION = "1.14"
CAP_REQUIRED_API_VERSION = "1.6"
SAN_REQUIRED_API_VERSION = "1.10"
NVME_API_VERSION = "1.16"
PREFERRED_API_VERSION = "1.15"
P53_API_VERSION = "1.17"
ACTIVE_DR_API = "1.19"
V6_MINIMUM_API_VERSION = "2.2"
FILES_API_VERSION = "2.3"
FC_REPL_API_VERSION = "2.4"
ENCRYPTION_STATUS_API_VERSION = "2.6"
DIR_QUOTA_API_VERSION = "2.7"
SHARED_CAP_API_VERSION = "2.9"
PURE_OUI = "naa.624a9370"
SAFE_MODE_VERSION = "2.10"
PER_PG_VERSION = "2.13"
SAML2_VERSION = "2.11"
NFS_USER_MAP_VERSION = "2.15"
DEFAULT_PROT_API_VERSION = "2.16"
VM_VERSION = "2.14"
VLAN_VERSION = "2.17"
NEIGHBOR_API_VERSION = "2.22"
POD_QUOTA_VERSION = "2.23"
AUTODIR_API_VERSION = "2.24"
SUBS_API_VERSION = "2.26"
NSID_API_VERSION = "2.27"
NFS_SECURITY_VERSION = "2.29"
UPTIME_API_VERSION = "2.30"
TLS_CONNECTION_API_VERSION = "2.33"
PWD_POLICY_API_VERSION = "2.34"
RA_API_VERSION = "2.35"
DSROLE_POLICY_API_VERSION = "2.36"
CONTEXT_API_VERSION = "2.38"


def _is_cbs(array):
    """Is the selected array a Cloud Block Store"""
    model = list(array.get_hardware(filter="type='controller'").items)[0].model
    is_cbs = bool("CBS" in model)
    return is_cbs


def generate_default_dict(module, array):
    default_info = {}
    defaults = array.get()
    api_version = array._list_available_rest_versions()
    arrayv6 = get_array(module)
    default_info["api_versions"] = api_version
    if FILES_API_VERSION in api_version:
        if VM_VERSION in api_version:
            default_info["virtual_machines"] = len(
                arrayv6.get_virtual_machines(vm_type="vvol").items
            )
            default_info["virtual_machine_snaps"] = len(
                arrayv6.get_virtual_machine_snapshots(vm_type="vvol").items
            )
        default_info["snapshot_policies"] = len(arrayv6.get_policies_snapshot().items)
        default_info["nfs_policies"] = len(arrayv6.get_policies_nfs().items)
        default_info["smb_policies"] = len(arrayv6.get_policies_smb().items)
        default_info["filesystems"] = len(arrayv6.get_file_systems().items)
        default_info["directories"] = len(arrayv6.get_directories().items)
        default_info["exports"] = len(arrayv6.get_directory_exports().items)
        default_info["directory_snapshots"] = len(
            arrayv6.get_directory_snapshots().items
        )
        if DIR_QUOTA_API_VERSION in api_version:
            default_info["quota_policies"] = len(arrayv6.get_policies_quota().items)
        if PWD_POLICY_API_VERSION in api_version:
            default_info["password_policies"] = len(
                arrayv6.get_policies_password().items
            )
        if ENCRYPTION_STATUS_API_VERSION in api_version:
            array_data = list(arrayv6.get_arrays().items)[0]
            encryption = array_data.encryption
            default_info["encryption_enabled"] = encryption.data_at_rest.enabled
            if default_info["encryption_enabled"]:
                default_info["encryption_algorithm"] = encryption.data_at_rest.algorithm
                default_info["encryption_module_version"] = encryption.module_version
            eradication = array_data.eradication_config
            if SUBS_API_VERSION in api_version:
                default_info["service_mode"] = list(arrayv6.get_subscriptions().items)[
                    0
                ].service
                default_info["eradication_disabled_days_timer"] = int(
                    eradication.disabled_delay / SEC_TO_DAY
                )
                default_info["eradication_enabled_days_timer"] = int(
                    eradication.enabled_delay / SEC_TO_DAY
                )
            eradication_delay = getattr(eradication, "eradication_delay", None)
            if eradication_delay is not None:
                default_info["eradication_days_timer"] = int(
                    eradication_delay / SEC_TO_DAY
                )
            if SAFE_MODE_VERSION in api_version:
                if eradication.manual_eradication == "all-enabled":
                    default_info["safe_mode"] = "Disabled"
                else:
                    default_info["safe_mode"] = "Enabled"
            if UPTIME_API_VERSION in api_version:
                default_info["controller_uptime"] = []
                controllers = list(arrayv6.get_controllers().items)
                timenow = datetime.fromtimestamp(time.time())
                for controller in range(0, len(controllers)):
                    boottime = datetime.fromtimestamp(
                        controllers[controller].mode_since / 1000
                    )
                    delta = timenow - boottime
                    default_info["controller_uptime"].append(
                        {
                            "controller": controllers[controller].name,
                            "uptime": str(delta),
                        }
                    )
    if AC_REQUIRED_API_VERSION in api_version:
        default_info["volume_groups"] = len(array.list_vgroups())
        default_info["connected_arrays"] = len(array.list_array_connections())
        default_info["pods"] = len(array.list_pods())
        default_info["connection_key"] = array.get(connection_key=True)[
            "connection_key"
        ]
    if (
        TLS_CONNECTION_API_VERSION in api_version
        and default_info["connected_arrays"] > 0
    ):
        default_info["connection_paths"] = []
        connection_paths = list(arrayv6.get_array_connections_path().items)
        for path in range(0, len(connection_paths)):
            default_info["connection_paths"].append(
                {
                    connection_paths[path].name: {
                        "local_port": getattr(
                            connection_paths[path], "local_port", None
                        ),
                        "local_address": getattr(
                            connection_paths[path], "local_address", None
                        ),
                        "remote_port": getattr(
                            connection_paths[path], "remote_port", None
                        ),
                        "remote_address": getattr(
                            connection_paths[path], "remote_address", None
                        ),
                        "status": getattr(connection_paths[path], "status", None),
                        "transport": getattr(
                            connection_paths[path], "replication_transport", None
                        ),
                        "encryption": getattr(
                            connection_paths[path], "encryption", None
                        ),
                        "encryption_mode": getattr(
                            connection_paths[path], "encryption_mode", None
                        ),
                    }
                }
            )
    hosts = array.list_hosts()
    admins = array.list_admins()
    snaps = array.list_volumes(snap=True, pending=True)
    volumes = array.list_volumes(pending=True)
    pgroups = array.list_pgroups(pending=True)
    hgroups = array.list_hgroups()
    default_info["array_model"] = array.get(controllers=True)[0]["model"]
    default_info["array_name"] = defaults["array_name"]
    default_info["purity_version"] = defaults["version"]
    default_info["hosts"] = len(hosts)
    default_info["snapshots"] = len(snaps)
    default_info["volumes"] = len(volumes)
    default_info["protection_groups"] = len(pgroups)
    default_info["hostgroups"] = len(hgroups)
    default_info["admins"] = len(admins)
    default_info["remote_assist"] = list(arrayv6.get_support().items)[
        0
    ].remote_assist_status
    if RA_API_VERSION in api_version:
        ra_detail = list(arrayv6.get_support().items)[0]
        default_info["remote_assist_detail"] = {
            "remote_assist_duration": str(
                int(ra_detail.remote_assist_duration / 3600000)
            )
            + " hours",
        }
        if ra_detail.remote_assist_expires != 0:
            default_info["remote_assist_detail"]["remote_assist_expires"] = (
                time.strftime(
                    "%Y-%m-%d %H:%M:%S %Z",
                    time.gmtime(ra_detail.remote_assist_expires / 1000),
                )
            )
        else:
            default_info["remote_assist_detail"]["remote_assist_expires"] = None
        if ra_detail.remote_assist_opened != 0:
            default_info["remote_assist_detail"]["remote_assist_opened"] = (
                time.strftime(
                    "%Y-%m-%d %H:%M:%S %Z",
                    time.gmtime(ra_detail.remote_assist_opened / 1000),
                )
            )
        else:
            default_info["remote_assist_detail"]["remote_assist_opened"] = None
    if P53_API_VERSION in api_version:
        default_info["maintenance_window"] = array.list_maintenance_windows()
    return default_info


def generate_perf_dict(array):
    perf_info = {}
    api_version = array._list_available_rest_versions()
    if LATENCY_REQUIRED_API_VERSION in api_version:
        latency_info = array.get(action="monitor", latency=True)[0]
    perf_info = array.get(action="monitor")[0]
    perf_info["writes_per_sec"] = perf_info["writes_per_sec"]
    perf_info["reads_per_sec"] = perf_info["reads_per_sec"]

    perf_info["input_per_sec"] = perf_info["input_per_sec"]
    perf_info["output_per_sec"] = perf_info["output_per_sec"]

    if LATENCY_REQUIRED_API_VERSION in api_version:
        perf_info["san_usec_per_read_op"] = latency_info["san_usec_per_read_op"]
        perf_info["san_usec_per_write_op"] = latency_info["san_usec_per_write_op"]
        perf_info["queue_usec_per_read_op"] = latency_info["queue_usec_per_read_op"]
        perf_info["queue_usec_per_write_op"] = latency_info["queue_usec_per_write_op"]
        perf_info["qos_rate_limit_usec_per_read_op"] = latency_info[
            "qos_rate_limit_usec_per_read_op"
        ]
        perf_info["qos_rate_limit_usec_per_write_op"] = latency_info[
            "qos_rate_limit_usec_per_write_op"
        ]
        perf_info["local_queue_usec_per_op"] = perf_info["local_queue_usec_per_op"]
    perf_info["usec_per_read_op"] = perf_info["usec_per_read_op"]
    perf_info["usec_per_write_op"] = perf_info["usec_per_write_op"]
    perf_info["queue_depth"] = perf_info["queue_depth"]
    return perf_info


def generate_config_dict(module, array):
    config_info = {}
    api_version = array._list_available_rest_versions()
    config_info["console_lock"] = array.get_console_lock_status()["console_lock"]
    if NFS_USER_MAP_VERSION not in api_version:
        config_info["dns"] = array.get_dns()
    config_info["smtp"] = array.list_alert_recipients()
    config_info["snmp"] = array.list_snmp_managers()
    config_info["snmp_v3_engine_id"] = array.get_snmp_engine_id()["engine_id"]
    if V6_MINIMUM_API_VERSION in api_version:
        arrayv6 = get_array(module)
        smtp_info = list(arrayv6.get_smtp_servers().items)[0]
        config_info["smtp_servers"] = {
            "name": smtp_info.name,
            "password": getattr(smtp_info, "password", ""),
            "user_name": getattr(smtp_info, "user_name", ""),
            "encryption_mode": getattr(smtp_info, "encryption_mode", ""),
            "relay_host": getattr(smtp_info, "relay_host", ""),
            "sender_domain": getattr(smtp_info, "sender_domain", ""),
        }
        config_info["directory_service"] = {}
        services = list(arrayv6.get_directory_services().items)
        for service in range(0, len(services)):
            service_type = services[service].name
            config_info["directory_service"][service_type] = {
                "base_dn": getattr(services[service], "base_dn", "None"),
                "bind_user": getattr(services[service], "bind_user", "None"),
                "enabled": services[service].enabled,
                "services": services[service].services,
                "uris": services[service].uris,
            }
        config_info["directory_service_roles"] = {}
        roles = list(arrayv6.get_directory_services_roles().items)
        for role in range(0, len(roles)):
            role_name = roles[role].role.name
            config_info["directory_service_roles"][role_name] = {
                "group": getattr(roles[role], "group", None),
                "group_base": getattr(roles[role], "group_base", None),
                "management_access_policies": None,
            }
            if DSROLE_POLICY_API_VERSION in api_version:
                config_info["directory_service_roles"][role_name][
                    "management_access_policies"
                ] = getattr(roles[role].management_access_policies[0], "name", None)
        smi_s = list(arrayv6.get_smi_s().items)[0]
        config_info["smi-s"] = {
            "slp_enabled": smi_s.slp_enabled,
            "wbem_https_enabled": smi_s.wbem_https_enabled,
        }
        # Add additional SMI-S section to help with formatting
        # issues caused by `-` in the dict name.
        config_info["smi_s"] = {
            "slp_enabled": smi_s.slp_enabled,
            "wbem_https_enabled": smi_s.wbem_https_enabled,
        }
        if NFS_USER_MAP_VERSION in api_version:
            config_info["dns"] = {}
            dns_configs = list(arrayv6.get_dns().items)
            for config in range(0, len(dns_configs)):
                config_info["dns"][dns_configs[config].services[0]] = {
                    "nameservers": dns_configs[config].nameservers,
                    "domain": dns_configs[config].domain,
                }
                config_info["dns"][dns_configs[config].services[0]]["source"] = getattr(
                    dns_configs[config].source, "name", None
                )
        if SAML2_VERSION in api_version:
            config_info["saml2sso"] = {}
            saml2 = list(arrayv6.get_sso_saml2_idps().items)
            if saml2:
                config_info["saml2sso"] = {
                    "enabled": saml2[0].enabled,
                    "array_url": saml2[0].array_url,
                    "name": saml2[0].name,
                    "idp": {
                        "url": getattr(saml2[0].idp, "url", None),
                        "encrypt_enabled": saml2[0].idp.encrypt_assertion_enabled,
                        "sign_enabled": saml2[0].idp.sign_request_enabled,
                        "metadata_url": saml2[0].idp.metadata_url,
                    },
                    "sp": {
                        "decrypt_cred": getattr(
                            saml2[0].sp.decryption_credential, "name", None
                        ),
                        "sign_cred": getattr(
                            saml2[0].sp.signing_credential, "name", None
                        ),
                    },
                }
        if FILES_API_VERSION in api_version:
            config_info["active_directory"] = {}
            try:
                ad_accounts = list(arrayv6.get_active_directory().items)
                for ad_account in range(0, len(ad_accounts)):
                    ad_name = ad_accounts[ad_account].name
                    config_info["active_directory"][ad_name] = {
                        "computer_name": ad_accounts[ad_account].computer_name,
                        "domain": ad_accounts[ad_account].domain,
                        "directory_servers": getattr(
                            ad_accounts[ad_account], "directory_servers", None
                        ),
                        "kerberos_servers": getattr(
                            ad_accounts[ad_account], "kerberos_servers", None
                        ),
                        "service_principal_names": getattr(
                            ad_accounts[ad_account], "service_principal_names", None
                        ),
                        "tls": getattr(ad_accounts[ad_account], "tls", None),
                    }
            except Exception:
                module.warn("FA-Files is not enabled on this array")
        if DEFAULT_PROT_API_VERSION in api_version:
            config_info["default_protections"] = {}
            default_prots = list(arrayv6.get_container_default_protections().items)
            for prot in range(0, len(default_prots)):
                container = getattr(default_prots[prot], "name", "-")
                config_info["default_protections"][container] = {
                    "protections": [],
                    "type": getattr(default_prots[prot], "type", "array"),
                }
                for container_prot in range(
                    0, len(default_prots[prot].default_protections)
                ):
                    config_info["default_protections"][container]["protections"].append(
                        {
                            "type": default_prots[prot]
                            .default_protections[container_prot]
                            .type,
                            "name": default_prots[prot]
                            .default_protections[container_prot]
                            .name,
                        }
                    )
        if SUBS_API_VERSION in api_version:
            array_info = list(arrayv6.get_arrays().items)[0]
            config_info["ntp_keys"] = bool(
                getattr(array_info, "ntp_symmetric_key", None)
            )
            config_info["timezone"] = array_info.time_zone
    else:
        config_info["directory_service"] = {}
        config_info["directory_service"]["management"] = array.get_directory_service()
        if S3_REQUIRED_API_VERSION in api_version:
            config_info["directory_service_roles"] = {}
            roles = array.list_directory_service_roles()
            for role in range(0, len(roles)):
                role_name = roles[role]["name"]
                config_info["directory_service_roles"][role_name] = {
                    "group": roles[role]["group"],
                    "group_base": roles[role]["group_base"],
                }
        else:
            config_info["directory_service"].update(
                array.get_directory_service(groups=True)
            )
    config_info["ntp"] = array.get(ntpserver=True)["ntpserver"]
    config_info["syslog"] = array.get(syslogserver=True)["syslogserver"]
    config_info["phonehome"] = array.get(phonehome=True)["phonehome"]
    config_info["proxy"] = array.get(proxy=True)["proxy"]
    config_info["relayhost"] = array.get(relayhost=True)["relayhost"]
    config_info["senderdomain"] = array.get(senderdomain=True)["senderdomain"]
    config_info["idle_timeout"] = array.get(idle_timeout=True)["idle_timeout"]
    config_info["scsi_timeout"] = array.get(scsi_timeout=True)["scsi_timeout"]
    if S3_REQUIRED_API_VERSION in api_version:
        config_info["global_admin"] = array.get_global_admin_attributes()
        if (
            config_info["global_admin"]["lockout_duration"]
            and config_info["global_admin"]["lockout_duration"] > 0
        ):
            config_info["global_admin"]["lockout_duration"] = int(
                config_info["global_admin"]["lockout_duration"] / 1000
            )
    return config_info


def generate_filesystems_dict(array):
    files_info = {}
    filesystems = list(array.get_file_systems().items)
    for filesystem in range(0, len(filesystems)):
        fs_name = filesystems[filesystem].name
        files_info[fs_name] = {
            "destroyed": filesystems[filesystem].destroyed,
            "directories": {},
        }
        directories = list(array.get_directories(file_system_names=[fs_name]).items)
        for directory in range(0, len(directories)):
            d_name = directories[directory].directory_name
            files_info[fs_name]["directories"][d_name] = {
                "path": directories[directory].path,
                "data_reduction": directories[directory].space.data_reduction,
                "snapshots_space": getattr(
                    directories[directory].space, "snapshots", None
                ),
                "total_physical_space": getattr(
                    directories[directory].space, "total_physical", None
                ),
                "unique_space": getattr(directories[directory].space, "unique", None),
                "virtual_space": getattr(directories[directory].space, "virtual", None),
                "destroyed": directories[directory].destroyed,
                "full_name": directories[directory].name,
                "used_provisioned": getattr(
                    directories[directory].space, "used_provisioned", None
                ),
                "exports": [],
                "policies": [],
            }
            if LooseVersion(SUBS_API_VERSION) <= LooseVersion(array.get_rest_version()):
                files_info[fs_name]["directories"][d_name]["total_used"] = directories[
                    directory
                ].space.total_used
            policies = list(
                array.get_directories_policies(
                    member_names=[
                        files_info[fs_name]["directories"][d_name]["full_name"]
                    ]
                ).items
            )
            for policy in range(0, len(policies)):
                files_info[fs_name]["directories"][d_name]["policies"].append(
                    {
                        "enabled": policies[policy].enabled,
                        "policy": {
                            "name": policies[policy].policy.name,
                            "type": policies[policy].policy.resource_type,
                        },
                    }
                )
            exports = list(
                array.get_directory_exports(
                    directory_names=[
                        files_info[fs_name]["directories"][d_name]["full_name"]
                    ]
                ).items
            )
            for export in range(0, len(exports)):
                files_info[fs_name]["directories"][d_name]["exports"].append(
                    {
                        "enabled": exports[export].enabled,
                        "export_name": exports[export].export_name,
                        "policy": {
                            "name": exports[export].policy.name,
                            "type": exports[export].policy.resource_type,
                        },
                    }
                )
    return files_info


def generate_pgsnaps_dict(array):
    pgsnaps_info = {}
    snapshots = list(array.get_protection_group_snapshots().items)
    for snapshot in range(0, len(snapshots)):
        s_name = snapshots[snapshot].name
        pgsnaps_info[s_name] = {
            "destroyed": snapshots[snapshot].destroyed,
            "source": snapshots[snapshot].source.name,
            "suffix": snapshots[snapshot].suffix,
            "snapshot_space": snapshots[snapshot].space.snapshots,
            "used_provisioned": getattr(
                snapshots[snapshot].space, "used_provisioned", None
            ),
        }
        try:
            if pgsnaps_info[s_name]["destroyed"]:
                pgsnaps_info[s_name]["time_remaining"] = snapshots[
                    snapshot
                ].time_remaining
        except AttributeError:
            pass
        try:
            pgsnaps_info[s_name]["manual_eradication"] = snapshots[
                snapshot
            ].eradication_config.manual_eradication
        except AttributeError:
            pass
    return pgsnaps_info


def generate_dir_snaps_dict(array):
    dir_snaps_info = {}
    snapshots = list(array.get_directory_snapshots().items)
    for snapshot in range(0, len(snapshots)):
        s_name = snapshots[snapshot].name
        if hasattr(snapshots[snapshot], "suffix"):
            suffix = snapshots[snapshot].suffix
        else:
            suffix = snapshots[snapshot].name.split(".")[-1]
        dir_snaps_info[s_name] = {
            "destroyed": snapshots[snapshot].destroyed,
            "source": snapshots[snapshot].source.name,
            "suffix": suffix,
            "client_name": snapshots[snapshot].client_name,
            "snapshot_space": snapshots[snapshot].space.snapshots,
            "total_physical_space": snapshots[snapshot].space.total_physical,
            "unique_space": snapshots[snapshot].space.unique,
            "used_provisioned": getattr(
                snapshots[snapshot].space, "used_provisioned", None
            ),
        }
        if LooseVersion(SUBS_API_VERSION) <= LooseVersion(array.get_rest_version()):
            dir_snaps_info[s_name]["total_used"] = snapshots[snapshot].space.total_used
        try:
            dir_snaps_info[s_name]["policy"] = snapshots[snapshot].policy.name
        except Exception:
            dir_snaps_info[s_name]["policy"] = ""
        if dir_snaps_info[s_name]["destroyed"] or hasattr(
            snapshots[snapshot], "time_remaining"
        ):
            dir_snaps_info[s_name]["time_remaining"] = snapshots[
                snapshot
            ].time_remaining
    return dir_snaps_info


def generate_policies_dict(array, quota_available, autodir_available, nfs_user_mapping):
    policy_info = {}
    policies = list(array.get_policies().items)
    for policy in range(0, len(policies)):
        p_name = policies[policy].name
        policy_info[p_name] = {
            "type": policies[policy].policy_type,
            "enabled": policies[policy].enabled,
            "members": [],
            "rules": [],
        }
        members = list(array.get_directories_policies(policy_names=[p_name]).items)
        for member in range(0, len(members)):
            m_name = members[member].member.name
            policy_info[p_name]["members"].append(m_name)
        if policies[policy].policy_type == "smb":
            rules = list(
                array.get_policies_smb_client_rules(policy_names=[p_name]).items
            )
            for rule in range(0, len(rules)):
                smb_rules_dict = {
                    "client": rules[rule].client,
                    "smb_encryption_required": rules[rule].smb_encryption_required,
                    "anonymous_access_allowed": rules[rule].anonymous_access_allowed,
                }
                policy_info[p_name]["rules"].append(smb_rules_dict)
        if policies[policy].policy_type == "nfs":
            if nfs_user_mapping:
                nfs_policy = list(array.get_policies_nfs(names=[p_name]).items)[0]
                policy_info[p_name][
                    "user_mapping_enabled"
                ] = nfs_policy.user_mapping_enabled
                if LooseVersion(SUBS_API_VERSION) <= LooseVersion(
                    array.get_rest_version()
                ):
                    policy_info[p_name]["nfs_version"] = getattr(
                        nfs_policy, "nfs_version", None
                    )
                if LooseVersion(NFS_SECURITY_VERSION) <= LooseVersion(
                    array.get_rest_version()
                ):
                    policy_info[p_name]["security"] = getattr(
                        nfs_policy, "security", None
                    )
            rules = list(
                array.get_policies_nfs_client_rules(policy_names=[p_name]).items
            )
            for rule in range(0, len(rules)):
                nfs_rules_dict = {
                    "access": rules[rule].access,
                    "permission": rules[rule].permission,
                    "client": rules[rule].client,
                }
                if LooseVersion(SUBS_API_VERSION) <= LooseVersion(
                    array.get_rest_version()
                ):
                    nfs_rules_dict["nfs_version"] = rules[rule].nfs_version
                policy_info[p_name]["rules"].append(nfs_rules_dict)
        if policies[policy].policy_type == "snapshot":
            suffix_enabled = bool(
                LooseVersion(array.get_rest_version())
                >= LooseVersion(SHARED_CAP_API_VERSION)
            )
            rules = list(array.get_policies_snapshot_rules(policy_names=[p_name]).items)
            for rule in range(0, len(rules)):
                try:
                    snap_rules_dict = {
                        "at": str(int(rules[rule].at / 3600000)).zfill(2) + ":00",
                        "client_name": rules[rule].client_name,
                        "every": str(int(rules[rule].every / 60000)) + " mins",
                        "keep_for": str(int(rules[rule].keep_for / 60000)) + " mins",
                    }
                except AttributeError:
                    snap_rules_dict = {
                        "at": None,
                        "client_name": rules[rule].client_name,
                        "every": str(int(rules[rule].every / 60000)) + " mins",
                        "keep_for": str(int(rules[rule].keep_for / 60000)) + " mins",
                    }
                if suffix_enabled:
                    try:
                        snap_rules_dict["suffix"] = rules[rule].suffix
                    except AttributeError:
                        snap_rules_dict["suffix"] = ""
                policy_info[p_name]["rules"].append(snap_rules_dict)
        if policies[policy].policy_type == "quota" and quota_available:
            rules = list(array.get_policies_quota_rules(policy_names=[p_name]).items)
            for rule in range(0, len(rules)):
                quota_rules_dict = {
                    "enforced": rules[rule].enforced,
                    "quota_limit": rules[rule].quota_limit,
                    "notifications": rules[rule].notifications,
                }
                policy_info[p_name]["rules"].append(quota_rules_dict)
        if policies[policy].policy_type == "autodir" and autodir_available:
            pass  # there are currently no rules for autodir policies
        if policies[policy].policy_type == "password":
            pwd_policy = list(array.get_policies_password(names=[p_name]).items)[0]
            policy_info[p_name] |= {
                "enabled": pwd_policy.enabled,
                "enforce_dictionary_check": pwd_policy.enforce_dictionary_check,
                "enforce_username_check": pwd_policy.enforce_username_check,
                "lockout_duration": getattr(pwd_policy, "lockout_duration", None),
                "password_history": getattr(pwd_policy, "password_history", None),
                "min_character_groups": pwd_policy.min_character_groups,
                "min_characters_per_group": pwd_policy.min_characters_per_group,
                "min_password_length": pwd_policy.min_password_length,
            }
    return policy_info


def generate_clients_dict(array):
    clients_info = {}
    clients = list(array.get_api_clients().items)
    for client in range(0, len(clients)):
        c_name = clients[client].name
        clients_info[c_name] = {
            "enabled": clients[client].enabled,
            "TTL(seconds)": clients[client].access_token_ttl_in_ms / 1000,
            "key_id": clients[client].key_id,
            "client_id": clients[client].id,
            "max_role": clients[client].max_role,
            "public_key": clients[client].public_key,
        }
    return clients_info


def generate_admin_dict(array):
    admin_info = {}
    api_version = array._list_available_rest_versions()
    if ADMIN_API_VERSION in api_version:
        admins = array.list_admins()
        for admin in range(0, len(admins)):
            admin_name = admins[admin]["name"]
            admin_info[admin_name] = {
                "type": admins[admin]["type"],
                "role": admins[admin]["role"],
            }
    return admin_info


def generate_subnet_dict(array):
    sub_info = {}
    subnets = array.list_subnets()
    for sub in range(0, len(subnets)):
        sub_name = subnets[sub]["name"]
        sub_info[sub_name] = {
            "enabled": subnets[sub]["enabled"],
            "gateway": subnets[sub]["gateway"],
            "mtu": subnets[sub]["mtu"],
            "vlan": subnets[sub]["vlan"],
            "prefix": subnets[sub]["prefix"],
            "interfaces": subnets[sub]["interfaces"],
            "services": subnets[sub]["services"],
        }
    return sub_info


def generate_network_dict(module, array, performance):
    net_info = {}
    api_version = array._list_available_rest_versions()
    arrayv6 = get_array(module)
    ports = list(arrayv6.get_network_interfaces().items)
    for port in range(0, len(ports)):
        int_name = ports[port].name
        if ports[port].interface_type == "eth":
            net_info[int_name] = {
                "hwaddr": getattr(ports[port].eth, "mac_address", None),
                "mac_address": getattr(ports[port].eth, "mac_address", None),
                "mtu": getattr(ports[port].eth, "mtu", None),
                "enabled": ports[port].enabled,
                "speed": ports[port].speed,
                "address": getattr(ports[port].eth, "address", None),
                "subinterfaces": [],
                "slaves": [],
                "subnet": getattr(ports[port].eth.subnet, "name", None),
                "services": ports[port].services,
                "gateway": getattr(ports[port].eth, "gateway", None),
                "netmask": getattr(ports[port].eth, "netmask", None),
                "subtype": getattr(ports[port].eth, "subtype", None),
                "vlan": getattr(ports[port].eth, "vlan", None),
                "performance": [],
            }
            if ports[port].eth.subinterfaces:
                for subi in range(0, len(ports[port].eth.subinterfaces)):
                    net_info[int_name]["subinterfaces"].append(
                        ports[port].eth.subinterfaces[subi].name
                    )
                net_info[int_name]["slaves"] = net_info[int_name]["subinterfaces"]
        else:
            net_info[int_name] = {
                "port_name": ports[port].fc.wwn,
                "services": ports[port].services,
                "enabled": ports[port].enabled,
                "performance": [],
            }
    if performance:
        perf_stats = list(arrayv6.get_network_interfaces_performance().items)
        for perf_stat in range(0, len(perf_stats)):
            if perf_stats[perf_stat].interface_type == "fc":
                net_info[perf_stats[perf_stat].name]["performance"] = {
                    "received_bytes_per_sec": getattr(
                        perf_stats[perf_stat].fc, "received_bytes_per_sec", 0
                    ),
                    "received_crc_errors_per_sec": getattr(
                        perf_stats[perf_stat].fc, "received_crc_errors_per_sec", 0
                    ),
                    "received_frames_per_sec": getattr(
                        perf_stats[perf_stat].fc, "received_frames_per_sec", 0
                    ),
                    "received_link_failures_per_sec": getattr(
                        perf_stats[perf_stat].fc, "received_link_failures_per_sec", 0
                    ),
                    "received_loss_of_signal_per_sec": getattr(
                        perf_stats[perf_stat].fc, "received_loss_of_signal_per_sec", 0
                    ),
                    "received_loss_of_sync_per_sec": getattr(
                        perf_stats[perf_stat].fc, "received_loss_of_sync_per_sec", 0
                    ),
                    "total_errors_per_sec": getattr(
                        perf_stats[perf_stat].fc, "total_errors_per_sec", 0
                    ),
                    "transmitted_bytes_per_sec": getattr(
                        perf_stats[perf_stat].fc, "transmitted_bytes_per_sec", 0
                    ),
                    "transmitted_frames_per_sec": getattr(
                        perf_stats[perf_stat].fc, "transmitted_frames_per_sec", 0
                    ),
                    "transmitted_invalid_words_per_sec": getattr(
                        perf_stats[perf_stat].fc, "transmitted_invalid_words_per_sec", 0
                    ),
                }
            else:
                net_info[perf_stats[perf_stat].name]["performance"] = {
                    "received_bytes_per_sec": getattr(
                        perf_stats[perf_stat].eth, "received_bytes_per_sec", 0
                    ),
                    "received_crc_errors_per_sec": getattr(
                        perf_stats[perf_stat].eth, "received_crc_errors_per_sec", 0
                    ),
                    "received_frame_errors_per_sec": getattr(
                        perf_stats[perf_stat].eth, "received_frame_errors_per_sec", 0
                    ),
                    "received_packets_per_sec": getattr(
                        perf_stats[perf_stat].eth, "received_packets_per_sec", 0
                    ),
                    "total_errors_per_sec": getattr(
                        perf_stats[perf_stat].eth, "total_errors_per_sec", 0
                    ),
                    "transmitted_bytes_per_sec": getattr(
                        perf_stats[perf_stat].eth, "transmitted_bytes_per_sec", 0
                    ),
                    "transmitted_dropped_errors_per_sec": getattr(
                        perf_stats[perf_stat].eth,
                        "transmitted_dropped_errors_per_sec",
                        0,
                    ),
                    "transmitted_packets_per_sec": getattr(
                        perf_stats[perf_stat].eth, "transmitted_packets_per_sec", 0
                    ),
                    "rdma_received_req_cqe_errors_per_sec": getattr(
                        perf_stats[perf_stat].eth,
                        "rdma_received_req_cqe_errors_per_sec",
                        0,
                    ),
                    "rdma_received_sequence_errors_per_sec": getattr(
                        perf_stats[perf_stat].eth,
                        "rdma_received_sequence_errors_per_sec",
                        0,
                    ),
                    "rdma_transmitted_local_ack_timeout_errors_per_sec": getattr(
                        perf_stats[perf_stat].eth,
                        "rdma_transmitted_local_ack_timeout_errors_per_sec",
                        0,
                    ),
                    "flow_control_received_congestion_packets_per_sec": getattr(
                        perf_stats[perf_stat].eth,
                        "flow_control_received_congestion_packets_per_sec",
                        0,
                    ),
                    "flow_control_received_discarded_packets_per_sec": getattr(
                        perf_stats[perf_stat].eth,
                        "flow_control_received_discarded_packets_per_sec",
                        0,
                    ),
                    "flow_control_received_lossless_bytes_per_sec": getattr(
                        perf_stats[perf_stat].eth,
                        "flow_control_received_lossless_bytes_per_sec",
                        0,
                    ),
                    "flow_control_received_pause_frames_per_sec": getattr(
                        perf_stats[perf_stat].eth,
                        "flow_control_received_pause_frames_per_sec",
                        0,
                    ),
                    "flow_control_transmitted_congestion_packets_per_sec": getattr(
                        perf_stats[perf_stat].eth,
                        "flow_control_transmitted_congestion_packets_per_sec",
                        0,
                    ),
                    "flow_control_transmitted_discarded_packets_per_sec": getattr(
                        perf_stats[perf_stat].eth,
                        "flow_control_transmitted_discarded_packets_per_sec",
                        0,
                    ),
                    "flow_control_transmitted_lossless_bytes_per_sec": getattr(
                        perf_stats[perf_stat].eth,
                        "flow_control_transmitted_lossless_bytes_per_sec",
                        0,
                    ),
                    "flow_control_transmitted_pause_frames_per_sec": getattr(
                        perf_stats[perf_stat].eth,
                        "flow_control_transmitted_pause_frames_per_sec",
                        0,
                    ),
                }
    if NEIGHBOR_API_VERSION in api_version:
        neighbors = list(arrayv6.get_network_interfaces_neighbors().items)
        for neighbor in range(0, len(neighbors)):
            neighbor_info = neighbors[neighbor]
            int_name = neighbor_info.local_port.name
            try:
                net_info[int_name].update(
                    {
                        "neighbor": {
                            "initial_ttl_in_sec": neighbor_info.initial_ttl_in_sec,
                            "neighbor_port": {
                                "description": getattr(
                                    neighbor_info.neighbor_port, "description", None
                                ),
                                "name": getattr(
                                    neighbor_info.neighbor_chassis, "name", None
                                ),
                                "id": getattr(
                                    neighbor_info.neighbor_port.id, "value", None
                                ),
                            },
                            "neighbor_chassis": {
                                "addresses": getattr(
                                    neighbor_info.neighbor_chassis, "addresses", None
                                ),
                                "description": getattr(
                                    neighbor_info.neighbor_chassis, "description", None
                                ),
                                "name": getattr(
                                    neighbor_info.neighbor_chassis, "name", None
                                ),
                                "bridge": {
                                    "enabled": getattr(
                                        neighbor_info.neighbor_chassis.bridge,
                                        "enabled",
                                        False,
                                    ),
                                    "supported": getattr(
                                        neighbor_info.neighbor_chassis.bridge,
                                        "supported",
                                        False,
                                    ),
                                },
                                "repeater": {
                                    "enabled": getattr(
                                        neighbor_info.neighbor_chassis.repeater,
                                        "enabled",
                                        False,
                                    ),
                                    "supported": getattr(
                                        neighbor_info.neighbor_chassis.repeater,
                                        "supported",
                                        False,
                                    ),
                                },
                                "router": {
                                    "enabled": getattr(
                                        neighbor_info.neighbor_chassis.router,
                                        "enabled",
                                        False,
                                    ),
                                    "supported": getattr(
                                        neighbor_info.neighbor_chassis.router,
                                        "supported",
                                        False,
                                    ),
                                },
                                "station_only": {
                                    "enabled": getattr(
                                        neighbor_info.neighbor_chassis.station_only,
                                        "enabled",
                                        False,
                                    ),
                                    "supported": getattr(
                                        neighbor_info.neighbor_chassis.station_only,
                                        "supported",
                                        False,
                                    ),
                                },
                                "telephone": {
                                    "enabled": getattr(
                                        neighbor_info.neighbor_chassis.telephone,
                                        "enabled",
                                        False,
                                    ),
                                    "supported": getattr(
                                        neighbor_info.neighbor_chassis.telephone,
                                        "supported",
                                        False,
                                    ),
                                },
                                "wlan_access_point": {
                                    "enabled": getattr(
                                        neighbor_info.neighbor_chassis.wlan_access_point,
                                        "enabled",
                                        False,
                                    ),
                                    "supported": getattr(
                                        neighbor_info.neighbor_chassis.wlan_access_point,
                                        "supported",
                                        False,
                                    ),
                                },
                                "docsis_cable_device": {
                                    "enabled": getattr(
                                        neighbor_info.neighbor_chassis.docsis_cable_device,
                                        "enabled",
                                        False,
                                    ),
                                    "supported": getattr(
                                        neighbor_info.neighbor_chassis.docsis_cable_device,
                                        "supported",
                                        False,
                                    ),
                                },
                                "id": {
                                    "type": getattr(
                                        neighbor_info.neighbor_chassis.id,
                                        "type",
                                        None,
                                    ),
                                    "value": getattr(
                                        neighbor_info.neighbor_chassis.id,
                                        "value",
                                        None,
                                    ),
                                },
                            },
                        }
                    }
                )
            except KeyError:
                net_info[int_name] = {
                    "hwaddr": None,
                    "mtu": None,
                    "enabled": None,
                    "speed": None,
                    "address": None,
                    "slaves": None,
                    "services": None,
                    "gateway": None,
                    "netmask": None,
                    "subnet": None,
                    "neighbor": {
                        "initial_ttl_in_sec": neighbor_info.initial_ttl_in_sec,
                        "neighbor_port": {
                            "description": getattr(
                                neighbor_info.neighbor_port, "description", None
                            ),
                            "name": getattr(
                                neighbor_info.neighbor_chassis, "name", None
                            ),
                            "id": getattr(
                                neighbor_info.neighbor_port.id, "value", None
                            ),
                        },
                        "neighbor_chassis": {
                            "addresses": getattr(
                                neighbor_info.neighbor_chassis, "addresses", None
                            ),
                            "description": getattr(
                                neighbor_info.neighbor_chassis, "description", None
                            ),
                            "name": getattr(
                                neighbor_info.neighbor_chassis, "name", None
                            ),
                            "bridge": {
                                "enabled": getattr(
                                    neighbor_info.neighbor_chassis.bridge,
                                    "enabled",
                                    False,
                                ),
                                "supported": getattr(
                                    neighbor_info.neighbor_chassis.bridge,
                                    "supported",
                                    False,
                                ),
                            },
                            "repeater": {
                                "enabled": getattr(
                                    neighbor_info.neighbor_chassis.repeater,
                                    "enabled",
                                    False,
                                ),
                                "supported": getattr(
                                    neighbor_info.neighbor_chassis.repeater,
                                    "supported",
                                    False,
                                ),
                            },
                            "router": {
                                "enabled": getattr(
                                    neighbor_info.neighbor_chassis.router,
                                    "enabled",
                                    False,
                                ),
                                "supported": getattr(
                                    neighbor_info.neighbor_chassis.router,
                                    "supported",
                                    False,
                                ),
                            },
                            "station_only": {
                                "enabled": getattr(
                                    neighbor_info.neighbor_chassis.station_only,
                                    "enabled",
                                    False,
                                ),
                                "supported": getattr(
                                    neighbor_info.neighbor_chassis.station_only,
                                    "supported",
                                    False,
                                ),
                            },
                            "telephone": {
                                "enabled": getattr(
                                    neighbor_info.neighbor_chassis.telephone,
                                    "enabled",
                                    False,
                                ),
                                "supported": getattr(
                                    neighbor_info.neighbor_chassis.telephone,
                                    "supported",
                                    False,
                                ),
                            },
                            "wlan_access_point": {
                                "enabled": getattr(
                                    neighbor_info.neighbor_chassis.wlan_access_point,
                                    "enabled",
                                    False,
                                ),
                                "supported": getattr(
                                    neighbor_info.neighbor_chassis.wlan_access_point,
                                    "supported",
                                    False,
                                ),
                            },
                            "docsis_cable_device": {
                                "enabled": getattr(
                                    neighbor_info.neighbor_chassis.docsis_cable_device,
                                    "enabled",
                                    False,
                                ),
                                "supported": getattr(
                                    neighbor_info.neighbor_chassis.docsis_cable_device,
                                    "supported",
                                    False,
                                ),
                            },
                            "id": {
                                "type": getattr(
                                    neighbor_info.neighbor_chassis.id,
                                    "type",
                                    None,
                                ),
                                "value": getattr(
                                    neighbor_info.neighbor_chassis.id,
                                    "value",
                                    None,
                                ),
                            },
                        },
                    },
                }

    return net_info


def generate_capacity_dict(module, array):
    capacity_info = {}
    api_version = array._list_available_rest_versions()
    if V6_MINIMUM_API_VERSION in api_version:
        new_version = bool(SHARED_CAP_API_VERSION in api_version)
        arrayv6 = get_array(module)
        total_capacity = list(arrayv6.get_arrays().items)[0].capacity
        capacity = list(arrayv6.get_arrays_space().items)[0]
        capacity_info["total_capacity"] = total_capacity
        if new_version:
            capacity_info["provisioned_space"] = getattr(
                capacity.space, "total_provisioned", 0
            )
            capacity_info["free_space"] = total_capacity - getattr(
                capacity.space, "total_physical", 0
            )
            capacity_info["data_reduction"] = getattr(
                capacity.space, "data_reduction", 0
            )
            capacity_info["system_space"] = getattr(capacity.space, "system", 0)
            capacity_info["volume_space"] = getattr(capacity.space, "unique", 0)
            capacity_info["shared_space"] = getattr(capacity.space, "shared", 0)
            capacity_info["snapshot_space"] = getattr(capacity.space, "snapshots", 0)
            capacity_info["thin_provisioning"] = getattr(
                capacity.space, "thin_provisioning", 0
            )
            capacity_info["total_reduction"] = getattr(
                capacity.space, "total_reduction", 0
            )
            capacity_info["replication"] = getattr(capacity.space, "replication", 0)
            capacity_info["shared_effective"] = getattr(
                capacity.space, "shared_effective", 0
            )
            capacity_info["snapshots_effective"] = getattr(
                capacity.space, "snapshots_effective", 0
            )
            capacity_info["unique_effective"] = getattr(
                capacity.space, "total_effective", 0
            )
            capacity_info["total_effective"] = getattr(
                capacity.space, "total_effective", 0
            )
            capacity_info["used_provisioned"] = getattr(
                capacity.space, "used_provisioned", 0
            )
            if SUBS_API_VERSION in api_version:
                capacity_info["total_used"] = capacity.space.total_used
        else:
            capacity_info["provisioned_space"] = capacity.space["total_provisioned"]
            capacity_info["free_space"] = (
                total_capacity - capacity.space["total_physical"]
            )
            capacity_info["data_reduction"] = capacity.space["data_reduction"]
            capacity_info["system_space"] = capacity.space["system"]
            capacity_info["volume_space"] = capacity.space["unique"]
            capacity_info["shared_space"] = capacity.space["shared"]
            capacity_info["snapshot_space"] = capacity.space["snapshots"]
            capacity_info["thin_provisioning"] = capacity.space["thin_provisioning"]
            capacity_info["total_reduction"] = capacity.space["total_reduction"]
            capacity_info["replication"] = capacity.space["replication"]
        if NFS_SECURITY_VERSION in api_version and _is_cbs(arrayv6):
            cloud = list(arrayv6.get_arrays_cloud_capacity().items)[0]
            capacity_info["cloud_capacity"] = {
                "current_capacity": cloud.current_capacity,
                "requested_capacity": cloud.requested_capacity,
                "status": cloud.status,
            }
    elif CAP_REQUIRED_API_VERSION in api_version:
        volumes = array.list_volumes(pending=True)
        capacity_info["provisioned_space"] = sum(item["size"] for item in volumes)
        capacity = array.get(space=True)
        total_capacity = capacity[0]["capacity"]
        used_space = capacity[0]["total"]
        capacity_info["free_space"] = total_capacity - used_space
        capacity_info["total_capacity"] = total_capacity
        capacity_info["data_reduction"] = capacity[0]["data_reduction"]
        capacity_info["system_space"] = capacity[0]["system"]
        capacity_info["volume_space"] = capacity[0]["volumes"]
        capacity_info["shared_space"] = capacity[0]["shared_space"]
        capacity_info["snapshot_space"] = capacity[0]["snapshots"]
        capacity_info["thin_provisioning"] = capacity[0]["thin_provisioning"]
        capacity_info["total_reduction"] = capacity[0]["total_reduction"]
    return capacity_info


def generate_snap_dict(module, array):
    snap_info = {}
    api_version = array._list_available_rest_versions()
    if FC_REPL_API_VERSION in api_version:
        arrayv6 = get_array(module)
        snapsv6 = list(arrayv6.get_volume_snapshots(destroyed=False).items)
    snaps = array.list_volumes(snap=True)
    for snap in range(0, len(snaps)):
        snapshot = snaps[snap]["name"]
        snap_info[snapshot] = {
            "size": snaps[snap]["size"],
            "source": snaps[snap]["source"],
            "created": snaps[snap]["created"],
            "created_epoch": int(
                time.mktime(time.strptime(snaps[snap]["created"], "%Y-%m-%dT%H:%M:%SZ"))
            ),
            "tags": [],
            "is_local": True,
            "remote": [],
        }
        if ":" in snapshot and "::" not in snapshot:
            snap_info[snapshot]["is_local"] = False
    if FC_REPL_API_VERSION in api_version:
        for snap in range(0, len(snapsv6)):
            snapshot = snapsv6[snap].name
            snap_info[snapshot]["snapshot_space"] = snapsv6[snap].space.snapshots
            snap_info[snapshot]["used_provisioned"] = (
                getattr(snapsv6[snap].space, "used_provisioned", None),
            )
            snap_info[snapshot]["total_physical"] = snapsv6[snap].space.total_physical
            snap_info[snapshot]["total_provisioned"] = snapsv6[
                snap
            ].space.total_provisioned
            snap_info[snapshot]["unique_space"] = snapsv6[snap].space.unique
            if SHARED_CAP_API_VERSION in api_version:
                snap_info[snapshot]["snapshots_effective"] = getattr(
                    snapsv6[snap].space, "snapshots_effective", None
                )
            if SUBS_API_VERSION in api_version:
                snap_info[snapshot]["total_used"] = snapsv6[snap].space.total_used
        offloads = list(arrayv6.get_offloads().items)
        for offload in range(0, len(offloads)):
            offload_name = offloads[offload].name
            check_offload = arrayv6.get_remote_volume_snapshots(on=offload_name)
            if check_offload.status_code == 200:
                remote_snaps = list(
                    arrayv6.get_remote_volume_snapshots(
                        on=offload_name, destroyed=False
                    ).items
                )
                for remote_snap in range(0, len(remote_snaps)):
                    remote_snap_name = remote_snaps[remote_snap].name.split(":")[1]
                    remote_transfer = list(
                        arrayv6.get_remote_volume_snapshots_transfer(
                            on=offload_name, names=[remote_snaps[remote_snap].name]
                        ).items
                    )[0]
                    remote_dict = {
                        "source": remote_snaps[remote_snap].source.name,
                        "suffix": remote_snaps[remote_snap].suffix,
                        "size": remote_snaps[remote_snap].provisioned,
                        "data_transferred": remote_transfer.data_transferred,
                        "completed": time.strftime(
                            "%Y-%m-%d %H:%M:%S",
                            time.gmtime(remote_transfer.completed / 1000),
                        )
                        + " UTC",
                        "physical_bytes_written": remote_transfer.physical_bytes_written,
                        "progress": remote_transfer.progress,
                        "created": time.strftime(
                            "%Y-%m-%d %H:%M:%S",
                            time.gmtime(remote_snaps[remote_snap].created / 1000),
                        )
                        + " UTC",
                    }
                    try:
                        snap_info[remote_snap_name]["remote"].append(remote_dict)
                    except KeyError:
                        snap_info[remote_snap_name] = {"remote": []}
                        snap_info[remote_snap_name]["remote"].append(remote_dict)
    if ACTIVE_DR_API in api_version:
        snaptags = array.list_volumes(snap=True, tags=True, namespace="*")
        for snaptag in range(0, len(snaptags)):
            if snaptags[snaptag]["namespace"] != "vasa-integration.purestorage.com":
                snapname = snaptags[snaptag]["name"]
                tagdict = {
                    "key": snaptags[snaptag]["key"],
                    "value": snaptags[snaptag]["value"],
                    "namespace": snaptags[snaptag]["namespace"],
                }
                snap_info[snapname]["tags"].append(tagdict)
    return snap_info


def generate_del_snap_dict(module, array):
    snap_info = {}
    api_version = array._list_available_rest_versions()
    if FC_REPL_API_VERSION in api_version:
        arrayv6 = get_array(module)
        snapsv6 = list(arrayv6.get_volume_snapshots(destroyed=True).items)
    snaps = array.list_volumes(snap=True, pending_only=True)
    for snap in range(0, len(snaps)):
        snapshot = snaps[snap]["name"]
        snap_info[snapshot] = {
            "size": snaps[snap]["size"],
            "source": snaps[snap]["source"],
            "created": snaps[snap]["created"],
            "time_remaining": snaps[snap]["time_remaining"],
            "tags": [],
            "remote": [],
        }
    if FC_REPL_API_VERSION in api_version:
        for snap in range(0, len(snapsv6)):
            snapshot = snapsv6[snap].name
            snap_info[snapshot]["snapshot_space"] = snapsv6[snap].space.snapshots
            snap_info[snapshot]["used_provisioned"] = (
                getattr(snapsv6[snap].space, "used_provisioned", None),
            )
            snap_info[snapshot]["total_physical"] = snapsv6[snap].space.total_physical
            snap_info[snapshot]["total_provisioned"] = snapsv6[
                snap
            ].space.total_provisioned
            snap_info[snapshot]["unique_space"] = snapsv6[snap].space.unique
            if SUBS_API_VERSION in api_version:
                snap_info[snapshot]["total_used"] = snapsv6[snap].space.total_used
        offloads = list(arrayv6.get_offloads().items)
        for offload in range(0, len(offloads)):
            offload_name = offloads[offload].name
            check_offload = arrayv6.get_remote_volume_snapshots(on=offload_name)
            if check_offload.status_code == 200:
                remote_snaps = list(
                    arrayv6.get_remote_volume_snapshots(
                        on=offload_name, destroyed=True
                    ).items
                )
                for remote_snap in range(0, len(remote_snaps)):
                    remote_snap_name = remote_snaps[remote_snap].name.split(":")[1]
                    remote_transfer = list(
                        arrayv6.get_remote_volume_snapshots_transfer(
                            on=offload_name, names=[remote_snaps[remote_snap].name]
                        ).items
                    )[0]
                    remote_dict = {
                        "source": remote_snaps[remote_snap].source.name,
                        "suffix": remote_snaps[remote_snap].suffix,
                        "size": remote_snaps[remote_snap].provisioned,
                        "data_transferred": remote_transfer.data_transferred,
                        "completed": time.strftime(
                            "%Y-%m-%d %H:%M:%S",
                            time.gmtime(remote_transfer.completed / 1000),
                        )
                        + " UTC",
                        "physical_bytes_written": remote_transfer.physical_bytes_written,
                        "progress": remote_transfer.progress,
                        "created": time.strftime(
                            "%Y-%m-%d %H:%M:%S",
                            time.gmtime(remote_snaps[remote_snap].created / 1000),
                        )
                        + " UTC",
                    }
                    try:
                        snap_info[remote_snap_name]["remote"].append(remote_dict)
                    except KeyError:
                        snap_info[remote_snap_name] = {"remote": []}
                        snap_info[remote_snap_name]["remote"].append(remote_dict)
    if ACTIVE_DR_API in api_version:
        snaptags = array.list_volumes(
            snap=True, tags=True, pending_only=True, namespace="*"
        )
        for snaptag in range(0, len(snaptags)):
            if snaptags[snaptag]["namespace"] != "vasa-integration.purestorage.com":
                snapname = snaptags[snaptag]["name"]
                tagdict = {
                    "key": snaptags[snaptag]["key"],
                    "value": snaptags[snaptag]["value"],
                    "namespace": snaptags[snaptag]["namespace"],
                }
                snap_info[snapname]["tags"].append(tagdict)
    return snap_info


def generate_del_vol_dict(module, array):
    volume_info = {}
    api_version = array._list_available_rest_versions()
    vols = array.list_volumes(pending_only=True)
    for vol in range(0, len(vols)):
        volume = vols[vol]["name"]
        volume_info[volume] = {
            "size": vols[vol]["size"],
            "source": vols[vol]["source"],
            "created": vols[vol]["created"],
            "serial": vols[vol]["serial"],
            "page83_naa": PURE_OUI + vols[vol]["serial"],
            "nvme_nguid": "eui.00"
            + vols[vol]["serial"][0:14].lower()
            + "24a937"
            + vols[vol]["serial"][-10:].lower(),
            "time_remaining": vols[vol]["time_remaining"],
            "tags": [],
        }
    if V6_MINIMUM_API_VERSION in api_version:
        arrayv6 = get_array(module)
        vols_space = list(arrayv6.get_volumes_space(destroyed=True).items)
        for vol in range(0, len(vols_space)):
            name = vols_space[vol].name
            volume_info[name]["snapshots_space"] = vols_space[vol].space.snapshots
            # Provide system as this matches the old naming convention
            volume_info[name]["system"] = vols_space[vol].space.unique
            volume_info[name]["unique_space"] = vols_space[vol].space.unique
            volume_info[name]["virtual_space"] = vols_space[vol].space.virtual
            volume_info[name]["total_physical_space"] = vols_space[
                vol
            ].space.total_physical
            volume_info[name]["data_reduction"] = vols_space[vol].space.data_reduction
            volume_info[name]["total_reduction"] = vols_space[vol].space.total_reduction
            volume_info[name]["total_provisioned"] = vols_space[
                vol
            ].space.total_provisioned
            volume_info[name]["thin_provisioning"] = vols_space[
                vol
            ].space.thin_provisioning
            if SHARED_CAP_API_VERSION in api_version:
                volume_info[name]["snapshots_effective"] = getattr(
                    vols_space[vol].space, "snapshots_effective", None
                )
                volume_info[name]["unique_effective"] = getattr(
                    vols_space[vol].space, "unique_effective", None
                )
                volume_info[name]["used_provisioned"] = (
                    getattr(vols_space[vol].space, "used_provisioned", None),
                )
            if SUBS_API_VERSION in api_version:
                volume_info[name]["total_used"] = vols_space[vol].space.total_used
    if ACTIVE_DR_API in api_version:
        voltags = array.list_volumes(tags=True, pending_only=True)
        for voltag in range(0, len(voltags)):
            if voltags[voltag]["namespace"] != "vasa-integration.purestorage.com":
                volume = voltags[voltag]["name"]
                tagdict = {
                    "key": voltags[voltag]["key"],
                    "value": voltags[voltag]["value"],
                    "copyable": voltags[voltag]["copyable"],
                    "namespace": voltags[voltag]["namespace"],
                }
                volume_info[volume]["tags"].append(tagdict)
    if V6_MINIMUM_API_VERSION in api_version:
        volumes = list(arrayv6.get_volumes(destroyed=True).items)
        for vol in range(0, len(volumes)):
            name = volumes[vol].name
            volume_info[name]["promotion_status"] = volumes[vol].promotion_status
            volume_info[name]["requested_promotion_state"] = volumes[
                vol
            ].requested_promotion_state
            if SAFE_MODE_VERSION in api_version:
                volume_info[name]["subtype"] = volumes[vol].subtype
                volume_info[name]["priority"] = volumes[vol].priority
                volume_info[name]["priority_adjustment"] = volumes[
                    vol
                ].priority_adjustment.priority_adjustment_operator + str(
                    volumes[vol].priority_adjustment.priority_adjustment_value
                )
    return volume_info


def generate_vol_dict(module, array, performance):
    volume_info = {}
    vols_space = array.list_volumes(space=True)
    vols = array.list_volumes()
    for vol in range(0, len(vols)):
        volume = vols[vol]["name"]
        volume_info[volume] = {
            "protocol_endpoint": False,
            "source": vols[vol]["source"],
            "size": vols[vol]["size"],
            "serial": vols[vol]["serial"],
            "page83_naa": PURE_OUI + vols[vol]["serial"],
            "nvme_nguid": "eui.00"
            + vols[vol]["serial"][0:14].lower()
            + "24a937"
            + vols[vol]["serial"][-10:].lower(),
            "tags": [],
            "hosts": [],
            "bandwidth": "",
            "iops_limit": "",
            "data_reduction": vols_space[vol]["data_reduction"],
            "thin_provisioning": vols_space[vol]["thin_provisioning"],
            "total_reduction": vols_space[vol]["total_reduction"],
            "performance": [],
        }
    api_version = array._list_available_rest_versions()
    if V6_MINIMUM_API_VERSION in api_version:
        arrayv6 = get_array(module)
        vols_space = list(arrayv6.get_volumes_space(destroyed=False).items)
        for vol in range(0, len(vols_space)):
            name = vols_space[vol].name
            volume_info[name]["snapshots_space"] = vols_space[vol].space.snapshots
            # Provide system as this matches the old naming convention
            volume_info[name]["system"] = vols_space[vol].space.unique
            volume_info[name]["unique_space"] = vols_space[vol].space.unique
            volume_info[name]["virtual_space"] = vols_space[vol].space.virtual
            volume_info[name]["total_physical_space"] = vols_space[
                vol
            ].space.total_physical
            if SHARED_CAP_API_VERSION in api_version:
                volume_info[name]["snapshots_effective"] = getattr(
                    vols_space[vol].space, "snapshots_effective", None
                )
                volume_info[name]["unique_effective"] = getattr(
                    vols_space[vol].space, "unique_effective", None
                )
                volume_info[name]["total_effective"] = getattr(
                    vols_space[vol].space, "total_effective", None
                )
                volume_info[name]["used_provisioned"] = (
                    getattr(vols_space[vol].space, "used_provisioned", None),
                )
            if SUBS_API_VERSION in api_version:
                volume_info[name]["total_used"] = vols_space[vol].space.total_used
    if AC_REQUIRED_API_VERSION in api_version:
        qvols = array.list_volumes(qos=True)
        for qvol in range(0, len(qvols)):
            volume = qvols[qvol]["name"]
            qos = qvols[qvol]["bandwidth_limit"]
            volume_info[volume]["bandwidth"] = qos
            if P53_API_VERSION in api_version:
                iops = qvols[qvol]["iops_limit"]
                volume_info[volume]["iops_limit"] = iops
        vvols = array.list_volumes(protocol_endpoint=True)
        for vvol in range(0, len(vvols)):
            volume = vvols[vvol]["name"]
            volume_info[volume] = {
                "protocol_endpoint": True,
                "host_encryption_key_status": None,
                "source": vvols[vvol]["source"],
                "serial": vvols[vvol]["serial"],
                "nvme_nguid": "eui.00"
                + vvols[vvol]["serial"][0:14].lower()
                + "24a937"
                + vvols[vvol]["serial"][-10:].lower(),
                "page83_naa": PURE_OUI + vvols[vvol]["serial"],
                "tags": [],
                "hosts": [],
            }
        if P53_API_VERSION in array._list_available_rest_versions():
            e2ees = array.list_volumes(host_encryption_key=True)
            for e2ee in range(0, len(e2ees)):
                volume = e2ees[e2ee]["name"]
                volume_info[volume]["host_encryption_key_status"] = e2ees[e2ee][
                    "host_encryption_key_status"
                ]
    if V6_MINIMUM_API_VERSION in api_version:
        volumes = list(arrayv6.get_volumes(destroyed=False).items)
        for vol in range(0, len(volumes)):
            name = volumes[vol].name
            volume_info[name]["promotion_status"] = volumes[vol].promotion_status
            volume_info[name]["requested_promotion_state"] = volumes[
                vol
            ].requested_promotion_state
            volume_info[name]["subtype"] = volumes[vol].subtype
            if SAFE_MODE_VERSION in api_version:
                volume_info[name]["priority"] = volumes[vol].priority
                volume_info[name]["priority_adjustment"] = volumes[
                    vol
                ].priority_adjustment.priority_adjustment_operator + str(
                    volumes[vol].priority_adjustment.priority_adjustment_value
                )
        if performance:
            vols_performance = list(
                arrayv6.get_volumes_performance(destroyed=False).items
            )
            for performance in range(0, len(vols_performance)):
                volume_info[vols_performance[performance].name]["performance"] = {
                    "bytes_per_mirrored_write": vols_performance[
                        performance
                    ].bytes_per_mirrored_write,
                    "bytes_per_op": vols_performance[performance].bytes_per_op,
                    "bytes_per_read": vols_performance[performance].bytes_per_read,
                    "bytes_per_write": vols_performance[performance].bytes_per_write,
                    "mirrored_write_bytes_per_sec": vols_performance[
                        performance
                    ].mirrored_write_bytes_per_sec,
                    "mirrored_writes_per_sec": vols_performance[
                        performance
                    ].mirrored_writes_per_sec,
                    "qos_rate_limit_usec_per_mirrored_write_op": vols_performance[
                        performance
                    ].qos_rate_limit_usec_per_mirrored_write_op,
                    "qos_rate_limit_usec_per_read_op": vols_performance[
                        performance
                    ].qos_rate_limit_usec_per_mirrored_write_op,
                    "qos_rate_limit_usec_per_write_op": vols_performance[
                        performance
                    ].qos_rate_limit_usec_per_read_op,
                    "queue_usec_per_mirrored_write_op": vols_performance[
                        performance
                    ].queue_usec_per_mirrored_write_op,
                    "queue_usec_per_read_op": vols_performance[
                        performance
                    ].queue_usec_per_read_op,
                    "queue_usec_per_write_op": vols_performance[
                        performance
                    ].queue_usec_per_write_op,
                    "read_bytes_per_sec": vols_performance[
                        performance
                    ].read_bytes_per_sec,
                    "reads_per_sec": vols_performance[performance].reads_per_sec,
                    "san_usec_per_mirrored_write_op": vols_performance[
                        performance
                    ].san_usec_per_mirrored_write_op,
                    "san_usec_per_read_op": vols_performance[
                        performance
                    ].san_usec_per_read_op,
                    "san_usec_per_write_op": vols_performance[
                        performance
                    ].san_usec_per_write_op,
                    "service_usec_per_mirrored_write_op": vols_performance[
                        performance
                    ].service_usec_per_mirrored_write_op,
                    "service_usec_per_read_op": vols_performance[
                        performance
                    ].service_usec_per_read_op,
                    "service_usec_per_write_op": vols_performance[
                        performance
                    ].service_usec_per_write_op,
                    "usec_per_mirrored_write_op": vols_performance[
                        performance
                    ].usec_per_mirrored_write_op,
                    "usec_per_read_op": vols_performance[performance].usec_per_read_op,
                    "usec_per_write_op": vols_performance[
                        performance
                    ].usec_per_write_op,
                    "write_bytes_per_sec": vols_performance[
                        performance
                    ].write_bytes_per_sec,
                    "writes_per_sec": vols_performance[performance].writes_per_sec,
                }
    cvols = array.list_volumes(connect=True)
    for cvol in range(0, len(cvols)):
        volume = cvols[cvol]["name"]
        voldict = {"host": cvols[cvol]["host"], "lun": cvols[cvol]["lun"]}
        volume_info[volume]["hosts"].append(voldict)
    if ACTIVE_DR_API in api_version:
        voltags = array.list_volumes(tags=True)
        for voltag in range(0, len(voltags)):
            if voltags[voltag]["namespace"] != "vasa-integration.purestorage.com":
                volume = voltags[voltag]["name"]
                tagdict = {
                    "key": voltags[voltag]["key"],
                    "value": voltags[voltag]["value"],
                    "copyable": voltags[voltag]["copyable"],
                    "namespace": voltags[voltag]["namespace"],
                }
                volume_info[volume]["tags"].append(tagdict)
    return volume_info


def generate_host_dict(module, array, performance):
    api_version = array._list_available_rest_versions()
    host_info = {}
    arrayv6 = get_array(module)
    if FC_REPL_API_VERSION in api_version:
        hostsv6 = list(arrayv6.get_hosts().items)
    hosts = array.list_hosts()
    for host in range(0, len(hosts)):
        hostname = hosts[host]["name"]
        tports = []
        all_tports = []
        host_all_info = None
        try:
            host_all_info = array.get_host(hostname, all=True)
        except purestorage.PureHTTPError as err:
            if err.code == 400:
                continue
        if host_all_info:
            for tport in range(0, len(host_all_info)):
                for itport in range(0, len(host_all_info[tport]["target_port"])):
                    tports.append(host_all_info[tport]["target_port"][itport])
            all_tports = list(dict.fromkeys(tports))
        host_info[hostname] = {
            "hgroup": hosts[host]["hgroup"],
            "iqn": hosts[host]["iqn"],
            "wwn": hosts[host]["wwn"],
            "personality": array.get_host(hostname, personality=True)["personality"],
            "target_port": all_tports,
            "volumes": [],
            "performance": [],
            "performance_balance": [],
        }
        if FC_REPL_API_VERSION in api_version:
            host_connections = list(
                arrayv6.get_connections(host_names=[hostname]).items
            )
            for connection in range(0, len(host_connections)):
                connection_dict = {
                    "hostgroup": getattr(
                        host_connections[connection].host_group, "name", ""
                    ),
                    "volume": host_connections[connection].volume.name,
                    "lun": getattr(host_connections[connection], "lun", ""),
                    "nsid": getattr(host_connections[connection], "nsid", ""),
                }
                host_info[hostname]["volumes"].append(connection_dict)
        else:
            host_connections = array.list_host_connections(hostname)
            for connection in range(0, len(host_connections)):
                connection_dict = {
                    "hostgroup": host_connections[connection]["hgroup"],
                    "volume": host_connections[connection]["vol"],
                    "lun": host_connections[connection]["lun"],
                }
                host_info[hostname]["volumes"].append(connection_dict)
        if host_info[hostname]["iqn"]:
            chap_data = array.get_host(hostname, chap=True)
            host_info[hostname]["target_user"] = chap_data["target_user"]
            host_info[hostname]["host_user"] = chap_data["host_user"]
        if NVME_API_VERSION in api_version:
            host_info[hostname]["nqn"] = hosts[host]["nqn"]
    if PREFERRED_API_VERSION in api_version:
        hosts = array.list_hosts(preferred_array=True)
        for host in range(0, len(hosts)):
            hostname = hosts[host]["name"]
            host_info[hostname]["preferred_array"] = hosts[host]["preferred_array"]
    if FC_REPL_API_VERSION in api_version:
        hosts_balance = list(arrayv6.get_hosts_performance_balance().items)
        hosts_performance = list(arrayv6.get_hosts_performance().items)
        for host in range(0, len(hostsv6)):
            if hostsv6[host].is_local:
                host_info[hostsv6[host].name]["port_connectivity"] = hostsv6[
                    host
                ].port_connectivity.details
                host_perf_balance = []
                for balance in range(0, len(hosts_balance)):
                    if hosts[host]["name"] == hosts_balance[balance].name:
                        host_balance = {
                            "fraction_relative_to_max": getattr(
                                hosts_balance[balance],
                                "fraction_relative_to_max",
                                None,
                            ),
                            "op_count": getattr(hosts_balance[balance], "op_count", 0),
                            "target": getattr(
                                hosts_balance[balance].target, "name", None
                            ),
                            "failed": bool(
                                getattr(hosts_balance[balance].target, "failover", 0)
                            ),
                        }
                        if host_balance["target"]:
                            host_perf_balance.append(host_balance)
                host_info[hosts[host]["name"]]["performance_balance"].append(
                    host_perf_balance
                )
                if performance:
                    for perf in range(0, len(hosts_performance)):
                        if ":" not in hosts_performance[perf].name:
                            host_info[hosts_performance[perf].name]["performance"] = {
                                "bytes_per_mirrored_write": hosts_performance[
                                    perf
                                ].bytes_per_mirrored_write,
                                "bytes_per_op": hosts_performance[perf].bytes_per_op,
                                "bytes_per_read": hosts_performance[
                                    perf
                                ].bytes_per_read,
                                "bytes_per_write": hosts_performance[
                                    perf
                                ].bytes_per_write,
                                "mirrored_write_bytes_per_sec": hosts_performance[
                                    perf
                                ].mirrored_write_bytes_per_sec,
                                "mirrored_writes_per_sec": hosts_performance[
                                    perf
                                ].mirrored_writes_per_sec,
                                "qos_rate_limit_usec_per_mirrored_write_op": hosts_performance[
                                    perf
                                ].qos_rate_limit_usec_per_mirrored_write_op,
                                "qos_rate_limit_usec_per_read_op": hosts_performance[
                                    perf
                                ].qos_rate_limit_usec_per_mirrored_write_op,
                                "qos_rate_limit_usec_per_write_op": hosts_performance[
                                    perf
                                ].qos_rate_limit_usec_per_read_op,
                                "queue_usec_per_mirrored_write_op": hosts_performance[
                                    perf
                                ].queue_usec_per_mirrored_write_op,
                                "queue_usec_per_read_op": hosts_performance[
                                    perf
                                ].queue_usec_per_read_op,
                                "queue_usec_per_write_op": hosts_performance[
                                    perf
                                ].queue_usec_per_write_op,
                                "read_bytes_per_sec": hosts_performance[
                                    perf
                                ].read_bytes_per_sec,
                                "reads_per_sec": hosts_performance[perf].reads_per_sec,
                                "san_usec_per_mirrored_write_op": hosts_performance[
                                    perf
                                ].san_usec_per_mirrored_write_op,
                                "san_usec_per_read_op": hosts_performance[
                                    perf
                                ].san_usec_per_read_op,
                                "san_usec_per_write_op": hosts_performance[
                                    perf
                                ].san_usec_per_write_op,
                                "service_usec_per_mirrored_write_op": hosts_performance[
                                    perf
                                ].service_usec_per_mirrored_write_op,
                                "service_usec_per_read_op": hosts_performance[
                                    perf
                                ].service_usec_per_read_op,
                                "service_usec_per_write_op": hosts_performance[
                                    perf
                                ].service_usec_per_write_op,
                                "usec_per_mirrored_write_op": hosts_performance[
                                    perf
                                ].usec_per_mirrored_write_op,
                                "usec_per_read_op": hosts_performance[
                                    perf
                                ].usec_per_read_op,
                                "usec_per_write_op": hosts_performance[
                                    perf
                                ].usec_per_write_op,
                                "write_bytes_per_sec": hosts_performance[
                                    perf
                                ].write_bytes_per_sec,
                                "writes_per_sec": hosts_performance[
                                    perf
                                ].writes_per_sec,
                            }
    if VLAN_VERSION in api_version:
        hosts = list(arrayv6.get_hosts().items)
        for host in range(0, len(hosts)):
            if DSROLE_POLICY_API_VERSION in api_version:
                host_info[hostname]["destroyed"] = hosts[host].destroyed
                if hosts[host].destroyed:
                    host_info[hostname]["time_remaining"] = hosts[host].time_remaining
            if hosts[host].is_local:
                hostname = hosts[host].name
                host_info[hostname]["vlan"] = getattr(hosts[host], "vlan", None)
    return host_info


def generate_del_pgroups_dict(module, array):
    pgroups_info = {}
    api_version = array._list_available_rest_versions()
    pgroups = array.list_pgroups(pending_only=True)
    if SHARED_CAP_API_VERSION in api_version:
        array_v6 = get_array(module)
        deleted_enabled = True
    else:
        deleted_enabled = False
    for pgroup in range(0, len(pgroups)):
        protgroup = pgroups[pgroup]["name"]
        pgroups_info[protgroup] = {
            "hgroups": pgroups[pgroup]["hgroups"],
            "hosts": pgroups[pgroup]["hosts"],
            "source": pgroups[pgroup]["source"],
            "targets": pgroups[pgroup]["targets"],
            "volumes": pgroups[pgroup]["volumes"],
            "time_remaining": pgroups[pgroup]["time_remaining"],
        }
        try:
            prot_sched = array.get_pgroup(protgroup, schedule=True, pending=True)
            prot_reten = array.get_pgroup(protgroup, retention=True, pending=True)
            snap_transfers = array.get_pgroup(
                protgroup, snap=True, transfer=True, pending=True
            )
        except purestorage.PureHTTPError as err:
            if err.code == 400:
                continue
        if prot_sched["snap_enabled"] or prot_sched["replicate_enabled"]:
            pgroups_info[protgroup]["snap_frequency"] = prot_sched["snap_frequency"]
            pgroups_info[protgroup]["replicate_frequency"] = prot_sched[
                "replicate_frequency"
            ]
            pgroups_info[protgroup]["snap_enabled"] = prot_sched["snap_enabled"]
            pgroups_info[protgroup]["replicate_enabled"] = prot_sched[
                "replicate_enabled"
            ]
            pgroups_info[protgroup]["snap_at"] = prot_sched["snap_at"]
            pgroups_info[protgroup]["replicate_at"] = prot_sched["replicate_at"]
            pgroups_info[protgroup]["replicate_blackout"] = prot_sched[
                "replicate_blackout"
            ]
            pgroups_info[protgroup]["per_day"] = prot_reten["per_day"]
            pgroups_info[protgroup]["target_per_day"] = prot_reten["target_per_day"]
            pgroups_info[protgroup]["target_days"] = prot_reten["target_days"]
            pgroups_info[protgroup]["days"] = prot_reten["days"]
            pgroups_info[protgroup]["all_for"] = prot_reten["all_for"]
            pgroups_info[protgroup]["target_all_for"] = prot_reten["target_all_for"]
        pgroups_info[protgroup]["snaps"] = {}
        for snap_transfer in range(0, len(snap_transfers)):
            snap = snap_transfers[snap_transfer]["name"]
            pgroups_info[protgroup]["snaps"][snap] = {
                "time_remaining": snap_transfers[snap_transfer]["time_remaining"],
                "created": snap_transfers[snap_transfer]["created"],
                "started": snap_transfers[snap_transfer]["started"],
                "completed": snap_transfers[snap_transfer]["completed"],
                "physical_bytes_written": snap_transfers[snap_transfer][
                    "physical_bytes_written"
                ],
                "data_transferred": snap_transfers[snap_transfer]["data_transferred"],
                "progress": snap_transfers[snap_transfer]["progress"],
            }
        if deleted_enabled:
            pgroups_info[protgroup]["deleted_volumes"] = []
            volumes = list(
                array_v6.get_protection_groups_volumes(group_names=[protgroup]).items
            )
            if volumes:
                for volume in range(0, len(volumes)):
                    if volumes[volume].member["destroyed"]:
                        pgroups_info[protgroup]["deleted_volumes"].append(
                            volumes[volume].member["name"]
                        )
            else:
                pgroups_info[protgroup]["deleted_volumes"] = None
        if PER_PG_VERSION in api_version:
            try:
                pgroups_info[protgroup]["retention_lock"] = list(
                    array_v6.get_protection_groups(names=[protgroup]).items
                )[0].retention_lock
                pgroups_info[protgroup]["manual_eradication"] = list(
                    array_v6.get_protection_groups(names=[protgroup]).items
                )[0].eradication_config.manual_eradication
            except Exception:
                pass
    if V6_MINIMUM_API_VERSION in api_version:
        pgroups = list(array_v6.get_protection_groups(destroyed=True).items)
        for pgroup in range(0, len(pgroups)):
            name = pgroups[pgroup].name
            pgroups_info[name]["snapshots"] = getattr(
                pgroups[pgroup].space, "snapshots", None
            )
            pgroups_info[name]["shared"] = getattr(
                pgroups[pgroup].space, "shared", None
            )
            pgroups_info[name]["data_reduction"] = getattr(
                pgroups[pgroup].space, "data_reduction", None
            )
            pgroups_info[name]["thin_provisioning"] = getattr(
                pgroups[pgroup].space, "thin_provisioning", None
            )
            pgroups_info[name]["total_physical"] = getattr(
                pgroups[pgroup].space, "total_physical", None
            )
            pgroups_info[name]["total_provisioned"] = getattr(
                pgroups[pgroup].space, "total_provisioned", None
            )
            pgroups_info[name]["total_reduction"] = getattr(
                pgroups[pgroup].space, "total_reduction", None
            )
            pgroups_info[name]["unique"] = getattr(
                pgroups[pgroup].space, "unique", None
            )
            pgroups_info[name]["virtual"] = getattr(
                pgroups[pgroup].space, "virtual", None
            )
            pgroups_info[name]["replication"] = getattr(
                pgroups[pgroup].space, "replication", None
            )
            pgroups_info[name]["used_provisioned"] = getattr(
                pgroups[pgroup].space, "used_provisioned", None
            )
    return pgroups_info


def generate_pgroups_dict(module, array):
    pgroups_info = {}
    api_version = array._list_available_rest_versions()
    pgroups = array.list_pgroups()
    if SHARED_CAP_API_VERSION in api_version:
        array_v6 = get_array(module)
        deleted_enabled = True
    else:
        deleted_enabled = False
    for pgroup in range(0, len(pgroups)):
        protgroup = pgroups[pgroup]["name"]
        pgroups_info[protgroup] = {
            "hgroups": pgroups[pgroup]["hgroups"],
            "hosts": pgroups[pgroup]["hosts"],
            "source": pgroups[pgroup]["source"],
            "targets": pgroups[pgroup]["targets"],
            "volumes": pgroups[pgroup]["volumes"],
        }
        try:
            prot_sched = array.get_pgroup(protgroup, schedule=True)
            prot_reten = array.get_pgroup(protgroup, retention=True)
            snap_transfers = array.get_pgroup(
                protgroup, snap=True, transfer=True, pending=True
            )
        except purestorage.PureHTTPError as err:
            if err.code == 400:
                continue
        if prot_sched["snap_enabled"] or prot_sched["replicate_enabled"]:
            pgroups_info[protgroup]["snap_frequency"] = prot_sched["snap_frequency"]
            pgroups_info[protgroup]["replicate_frequency"] = prot_sched[
                "replicate_frequency"
            ]
            pgroups_info[protgroup]["snap_enabled"] = prot_sched["snap_enabled"]
            pgroups_info[protgroup]["replicate_enabled"] = prot_sched[
                "replicate_enabled"
            ]
            pgroups_info[protgroup]["snap_at"] = prot_sched["snap_at"]
            pgroups_info[protgroup]["replicate_at"] = prot_sched["replicate_at"]
            pgroups_info[protgroup]["replicate_blackout"] = prot_sched[
                "replicate_blackout"
            ]
            pgroups_info[protgroup]["per_day"] = prot_reten["per_day"]
            pgroups_info[protgroup]["target_per_day"] = prot_reten["target_per_day"]
            pgroups_info[protgroup]["target_days"] = prot_reten["target_days"]
            pgroups_info[protgroup]["days"] = prot_reten["days"]
            pgroups_info[protgroup]["all_for"] = prot_reten["all_for"]
            pgroups_info[protgroup]["target_all_for"] = prot_reten["target_all_for"]
        pgroups_info[protgroup]["snaps"] = {}
        for snap_transfer in range(0, len(snap_transfers)):
            snap = snap_transfers[snap_transfer]["name"]
            pgroups_info[protgroup]["snaps"][snap] = {
                "time_remaining": snap_transfers[snap_transfer]["time_remaining"],
                "created": snap_transfers[snap_transfer]["created"],
                "started": snap_transfers[snap_transfer]["started"],
                "completed": snap_transfers[snap_transfer]["completed"],
                "physical_bytes_written": snap_transfers[snap_transfer][
                    "physical_bytes_written"
                ],
                "data_transferred": snap_transfers[snap_transfer]["data_transferred"],
                "progress": snap_transfers[snap_transfer]["progress"],
            }
        if deleted_enabled:
            pgroups_info[protgroup]["deleted_volumes"] = []
            volumes = list(
                array_v6.get_protection_groups_volumes(group_names=[protgroup]).items
            )
            if volumes:
                for volume in range(0, len(volumes)):
                    if volumes[volume].member["destroyed"]:
                        pgroups_info[protgroup]["deleted_volumes"].append(
                            volumes[volume].member["name"]
                        )
            else:
                pgroups_info[protgroup]["deleted_volumes"] = None
        if PER_PG_VERSION in api_version:
            try:
                pgroups_info[protgroup]["retention_lock"] = list(
                    array_v6.get_protection_groups(names=[protgroup]).items
                )[0].retention_lock
                pgroups_info[protgroup]["manual_eradication"] = list(
                    array_v6.get_protection_groups(names=[protgroup]).items
                )[0].eradication_config.manual_eradication
            except Exception:
                pass
    if V6_MINIMUM_API_VERSION in api_version:
        pgroups = list(array_v6.get_protection_groups(destroyed=False).items)
        for pgroup in range(0, len(pgroups)):
            name = pgroups[pgroup].name
            pgroups_info[name]["snapshots"] = getattr(
                pgroups[pgroup].space, "snapshots", None
            )
            pgroups_info[name]["shared"] = getattr(
                pgroups[pgroup].space, "shared", None
            )
            pgroups_info[name]["data_reduction"] = getattr(
                pgroups[pgroup].space, "data_reduction", None
            )
            pgroups_info[name]["thin_provisioning"] = getattr(
                pgroups[pgroup].space, "thin_provisioning", None
            )
            pgroups_info[name]["total_physical"] = getattr(
                pgroups[pgroup].space, "total_physical", None
            )
            pgroups_info[name]["total_provisioned"] = getattr(
                pgroups[pgroup].space, "total_provisioned", None
            )
            pgroups_info[name]["total_reduction"] = getattr(
                pgroups[pgroup].space, "total_reduction", None
            )
            pgroups_info[name]["unique"] = getattr(
                pgroups[pgroup].space, "unique", None
            )
            pgroups_info[name]["virtual"] = getattr(
                pgroups[pgroup].space, "virtual", None
            )
            pgroups_info[name]["replication"] = getattr(
                pgroups[pgroup].space, "replication", None
            )
            pgroups_info[name]["used_provisioned"] = getattr(
                pgroups[pgroup].space, "used_provisioned", None
            )
    return pgroups_info


def generate_rl_dict(module, array):
    rl_info = {}
    api_version = array._list_available_rest_versions()
    if ACTIVE_DR_API in api_version:
        try:
            rlinks = array.list_pod_replica_links()
            for rlink in range(0, len(rlinks)):
                link_name = rlinks[rlink]["local_pod_name"]
                if rlinks[rlink]["recovery_point"]:
                    since_epoch = rlinks[rlink]["recovery_point"] / 1000
                    recovery_datatime = time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(since_epoch)
                    )
                else:
                    recovery_datatime = None
                if rlinks[rlink]["lag"]:
                    lag = str(rlinks[rlink]["lag"] / 1000) + "s"
                rl_info[link_name] = {
                    "status": rlinks[rlink]["status"],
                    "direction": rlinks[rlink]["direction"],
                    "lag": lag,
                    "remote_pod_name": rlinks[rlink]["remote_pod_name"],
                    "remote_names": rlinks[rlink]["remote_names"],
                    "recovery_point": recovery_datatime,
                }
        except Exception:
            module.warn("Replica Links info requires purestorage SDK 1.19 or hisher")
    return rl_info


def generate_del_pods_dict(module, array):
    pods_info = {}
    api_version = array._list_available_rest_versions()
    if AC_REQUIRED_API_VERSION in api_version:
        pods = array.list_pods(mediator=True, pending_only=True)
        for pod in range(0, len(pods)):
            acpod = pods[pod]["name"]
            pods_info[acpod] = {
                "source": pods[pod]["source"],
                "arrays": pods[pod]["arrays"],
                "mediator": pods[pod]["mediator"],
                "mediator_version": pods[pod]["mediator_version"],
                "time_remaining": pods[pod]["time_remaining"],
            }
            if ACTIVE_DR_API in api_version:
                if pods_info[acpod]["arrays"][0]["frozen_at"]:
                    frozen_time = pods_info[acpod]["arrays"][0]["frozen_at"] / 1000
                    frozen_datetime = time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(frozen_time)
                    )
                    pods_info[acpod]["arrays"][0]["frozen_at"] = frozen_datetime
                pods_info[acpod]["link_source_count"] = pods[pod]["link_source_count"]
                pods_info[acpod]["link_target_count"] = pods[pod]["link_target_count"]
                pods_info[acpod]["promotion_status"] = pods[pod]["promotion_status"]
                pods_info[acpod]["requested_promotion_state"] = pods[pod][
                    "requested_promotion_state"
                ]
        if PREFERRED_API_VERSION in api_version:
            pods_fp = array.list_pods(failover_preference=True, pending_only=True)
            for pod in range(0, len(pods_fp)):
                acpod = pods_fp[pod]["name"]
                pods_info[acpod]["failover_preference"] = pods_fp[pod][
                    "failover_preference"
                ]
        if V6_MINIMUM_API_VERSION in api_version:
            arrayv6 = get_array(module)
            pods = list(arrayv6.get_pods(destroyed=True).items)
            for pod in range(0, len(pods)):
                name = pods[pod].name
                pods_info[name]["snapshots"] = getattr(
                    pods[pod].space, "snapshots", None
                )
                pods_info[name]["shared"] = getattr(pods[pod].space, "shared", None)
                pods_info[name]["data_reduction"] = getattr(
                    pods[pod].space, "data_reduction", None
                )
                pods_info[name]["thin_provisioning"] = getattr(
                    pods[pod].space, "thin_provisioning", None
                )
                pods_info[name]["total_physical"] = getattr(
                    pods[pod].space, "total_physical", None
                )
                pods_info[name]["total_provisioned"] = getattr(
                    pods[pod].space, "total_provisioned", None
                )
                pods_info[name]["total_reduction"] = getattr(
                    pods[pod].space, "total_reduction", None
                )
                pods_info[name]["unique"] = getattr(pods[pod].space, "unique", None)
                pods_info[name]["virtual"] = getattr(pods[pod].space, "virtual", None)
                pods_info[name]["replication"] = pods[pod].space.replication
                pods_info[name]["used_provisioned"] = getattr(
                    pods[pod].space, "used_provisioned", None
                )
                if POD_QUOTA_VERSION in api_version:
                    pods_info[name]["quota_limit"] = getattr(
                        pods[pod], "quota_limit", None
                    )
                if SUBS_API_VERSION in api_version:
                    pods_info[name]["total_used"] = pods[pod].space.total_used
    return pods_info


def generate_pods_dict(module, array, performance):
    pods_info = {}
    api_version = array._list_available_rest_versions()
    if AC_REQUIRED_API_VERSION in api_version:
        pods = array.list_pods(mediator=True)
        for pod in range(0, len(pods)):
            acpod = pods[pod]["name"]
            pods_info[acpod] = {
                "source": pods[pod]["source"],
                "arrays": pods[pod]["arrays"],
                "mediator": pods[pod]["mediator"],
                "mediator_version": pods[pod]["mediator_version"],
                "performance": [],
            }
            if ACTIVE_DR_API in api_version:
                if pods_info[acpod]["arrays"][0]["frozen_at"]:
                    frozen_time = pods_info[acpod]["arrays"][0]["frozen_at"] / 1000
                    frozen_datetime = time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(frozen_time)
                    )
                    pods_info[acpod]["arrays"][0]["frozen_at"] = frozen_datetime
                pods_info[acpod]["link_source_count"] = pods[pod]["link_source_count"]
                pods_info[acpod]["link_target_count"] = pods[pod]["link_target_count"]
                pods_info[acpod]["promotion_status"] = pods[pod]["promotion_status"]
                pods_info[acpod]["requested_promotion_state"] = pods[pod][
                    "requested_promotion_state"
                ]
        if PREFERRED_API_VERSION in api_version:
            pods_fp = array.list_pods(failover_preference=True)
            for pod in range(0, len(pods_fp)):
                acpod = pods_fp[pod]["name"]
                pods_info[acpod]["failover_preference"] = pods_fp[pod][
                    "failover_preference"
                ]
        if V6_MINIMUM_API_VERSION in api_version:
            arrayv6 = get_array(module)
            pods = list(arrayv6.get_pods(destroyed=False).items)
            for pod in range(0, len(pods)):
                name = pods[pod].name
                pods_info[name]["snapshots"] = getattr(
                    pods[pod].space, "snapshots", None
                )
                pods_info[name]["shared"] = getattr(pods[pod].space, "shared", None)
                pods_info[name]["data_reduction"] = getattr(
                    pods[pod].space, "data_reduction", None
                )
                pods_info[name]["thin_provisioning"] = getattr(
                    pods[pod].space, "thin_provisioning", None
                )
                pods_info[name]["total_physical"] = getattr(
                    pods[pod].space, "total_physical", None
                )
                pods_info[name]["total_provisioned"] = getattr(
                    pods[pod].space, "total_provisioned", None
                )
                pods_info[name]["total_reduction"] = getattr(
                    pods[pod].space, "total_reduction", None
                )
                pods_info[name]["unique"] = getattr(pods[pod].space, "unique", None)
                pods_info[name]["virtual"] = getattr(pods[pod].space, "virtual", None)
                pods_info[name]["replication"] = getattr(
                    pods[pod].space, "replication", None
                )
                pods_info[name]["used_provisioned"] = getattr(
                    pods[pod].space, "used_provisioned", None
                )
                if SUBS_API_VERSION in api_version:
                    pods_info[name]["total_used"] = pods[pod].space.total_used
            if performance:
                pods_performance = list(arrayv6.get_pods_performance().items)
                for performance in range(0, len(pods_performance)):
                    pods_info[pods_performance[performance].name]["performance"] = {
                        "bytes_per_mirrored_write": pods_performance[
                            performance
                        ].bytes_per_mirrored_write,
                        "bytes_per_op": pods_performance[performance].bytes_per_op,
                        "bytes_per_read": pods_performance[performance].bytes_per_read,
                        "bytes_per_write": pods_performance[
                            performance
                        ].bytes_per_write,
                        "mirrored_write_bytes_per_sec": pods_performance[
                            performance
                        ].mirrored_write_bytes_per_sec,
                        "mirrored_writes_per_sec": pods_performance[
                            performance
                        ].mirrored_writes_per_sec,
                        "others_per_sec": pods_performance[performance].others_per_sec,
                        "qos_rate_limit_usec_per_mirrored_write_op": pods_performance[
                            performance
                        ].qos_rate_limit_usec_per_mirrored_write_op,
                        "qos_rate_limit_usec_per_read_op": pods_performance[
                            performance
                        ].qos_rate_limit_usec_per_mirrored_write_op,
                        "qos_rate_limit_usec_per_write_op": pods_performance[
                            performance
                        ].qos_rate_limit_usec_per_read_op,
                        "queue_usec_per_mirrored_write_op": pods_performance[
                            performance
                        ].queue_usec_per_mirrored_write_op,
                        "queue_usec_per_read_op": pods_performance[
                            performance
                        ].queue_usec_per_read_op,
                        "queue_usec_per_write_op": pods_performance[
                            performance
                        ].queue_usec_per_write_op,
                        "read_bytes_per_sec": pods_performance[
                            performance
                        ].read_bytes_per_sec,
                        "reads_per_sec": pods_performance[performance].reads_per_sec,
                        "san_usec_per_mirrored_write_op": pods_performance[
                            performance
                        ].san_usec_per_mirrored_write_op,
                        "san_usec_per_read_op": pods_performance[
                            performance
                        ].san_usec_per_read_op,
                        "san_usec_per_write_op": pods_performance[
                            performance
                        ].san_usec_per_write_op,
                        "service_usec_per_mirrored_write_op": pods_performance[
                            performance
                        ].service_usec_per_mirrored_write_op,
                        "service_usec_per_read_op": pods_performance[
                            performance
                        ].service_usec_per_read_op,
                        "service_usec_per_write_op": pods_performance[
                            performance
                        ].service_usec_per_write_op,
                        "usec_per_mirrored_write_op": pods_performance[
                            performance
                        ].usec_per_mirrored_write_op,
                        "usec_per_read_op": pods_performance[
                            performance
                        ].usec_per_read_op,
                        "usec_per_write_op": pods_performance[
                            performance
                        ].usec_per_write_op,
                        "write_bytes_per_sec": pods_performance[
                            performance
                        ].write_bytes_per_sec,
                        "writes_per_sec": pods_performance[performance].writes_per_sec,
                    }
    return pods_info


def generate_conn_array_dict(module, array):
    conn_array_info = {}
    api_version = array._list_available_rest_versions()
    if FC_REPL_API_VERSION not in api_version:
        carrays = array.list_array_connections()
        for carray in range(0, len(carrays)):
            arrayname = carrays[carray]["array_name"]
            conn_array_info[arrayname] = {
                "array_id": carrays[carray]["id"],
                "throttled": carrays[carray]["throttled"],
                "version": carrays[carray]["version"],
                "type": carrays[carray]["type"],
                "mgmt_ip": carrays[carray]["management_address"],
                "repl_ip": carrays[carray]["replication_address"],
            }
            if P53_API_VERSION in api_version:
                conn_array_info[arrayname]["status"] = carrays[carray]["status"]
            else:
                conn_array_info[arrayname]["connected"] = carrays[carray]["connected"]
        throttles = array.list_array_connections(throttle=True)
        for throttle in range(0, len(throttles)):
            arrayname = throttles[throttle]["array_name"]
            if conn_array_info[arrayname]["throttled"]:
                conn_array_info[arrayname]["throttling"] = {
                    "default_limit": throttles[throttle]["default_limit"],
                    "window_limit": throttles[throttle]["window_limit"],
                    "window": throttles[throttle]["window"],
                }
    else:
        arrayv6 = get_array(module)
        carrays = list(arrayv6.get_array_connections().items)
        for carray in range(0, len(carrays)):
            arrayname = carrays[carray].name
            conn_array_info[arrayname] = {
                "array_id": carrays[carray].id,
                "version": getattr(carrays[carray], "version", None),
                "status": carrays[carray].status,
                "type": carrays[carray].type,
                "mgmt_ip": getattr(carrays[carray], "management_address", "-"),
                "repl_ip": getattr(carrays[carray], "replication_addresses", "-"),
                "transport": carrays[carray].replication_transport,
            }

            if bool(carrays[carray].throttle.to_dict()):
                conn_array_info[arrayname]["throttled"] = True
                conn_array_info[arrayname]["throttling"] = {}
                try:
                    if bool(carrays[carray].throttle.window):
                        conn_array_info[arrayname]["throttling"]["window"] = carrays[
                            carray
                        ].throttle.window.to_dict()
                except AttributeError:
                    pass
                try:
                    if bool(carrays[carray].throttle.default_limit):
                        conn_array_info[arrayname]["throttling"]["default_limit"] = (
                            carrays[carray].throttle.default_limit
                        )
                except AttributeError:
                    pass
                try:
                    if bool(carrays[carray].throttle.window_limit):
                        conn_array_info[arrayname]["throttling"]["window_limit"] = (
                            carrays[carray].throttle.window_limit
                        )
                except AttributeError:
                    pass
            else:
                conn_array_info[arrayname]["throttled"] = False
    return conn_array_info


def generate_apps_dict(array):
    apps_info = {}
    api_version = array._list_available_rest_versions()
    if SAN_REQUIRED_API_VERSION in api_version:
        apps = array.list_apps()
        for app in range(0, len(apps)):
            appname = apps[app]["name"]
            apps_info[appname] = {
                "version": apps[app]["version"],
                "status": apps[app]["status"],
                "description": apps[app]["description"],
            }
    if P53_API_VERSION in api_version:
        app_nodes = array.list_app_nodes()
        for app in range(0, len(app_nodes)):
            appname = app_nodes[app]["name"]
            apps_info[appname]["index"] = app_nodes[app]["index"]
            if DSROLE_POLICY_API_VERSION in api_version:
                apps_info[appname]["vnc"] = "Deprecated"
            else:
                apps_info[appname]["vnc"] = app_nodes[app]["vnc"]
    return apps_info


def generate_vgroups_dict(module, array, performance):
    vgroups_info = {}
    api_version = array._list_available_rest_versions()
    if AC_REQUIRED_API_VERSION in api_version:
        vgroups = array.list_vgroups(pending=False)
        for vgroup in range(0, len(vgroups)):
            virtgroup = vgroups[vgroup]["name"]
            vgroups_info[virtgroup] = {
                "volumes": vgroups[vgroup]["volumes"],
                "performance": [],
            }
    if V6_MINIMUM_API_VERSION in api_version:
        arrayv6 = get_array(module)
        vgroups = list(arrayv6.get_volume_groups(destroyed=False).items)
        for vgroup in range(0, len(vgroups)):
            name = vgroups[vgroup].name
            vgroups_info[name]["snapshots_space"] = vgroups[vgroup].space.snapshots
            # Provide system as this matches the old naming convention
            vgroups_info[name]["system"] = vgroups[vgroup].space.unique
            vgroups_info[name]["unique_space"] = vgroups[vgroup].space.unique
            vgroups_info[name]["virtual_space"] = vgroups[vgroup].space.virtual
            vgroups_info[name]["data_reduction"] = vgroups[vgroup].space.data_reduction
            vgroups_info[name]["total_reduction"] = vgroups[
                vgroup
            ].space.total_reduction
            vgroups_info[name]["total_provisioned"] = vgroups[
                vgroup
            ].space.total_provisioned
            vgroups_info[name]["thin_provisioning"] = vgroups[
                vgroup
            ].space.thin_provisioning
            vgroups_info[name]["used_provisioned"] = (
                getattr(vgroups[vgroup].space, "used_provisioned", None),
            )
            vgroups_info[name]["bandwidth_limit"] = getattr(
                vgroups[vgroup].qos, "bandwidth_limit", ""
            )
            vgroups_info[name]["iops_limit"] = getattr(
                vgroups[vgroup].qos, "iops_limit", ""
            )
            if SUBS_API_VERSION in api_version:
                vgroups_info[name]["total_used"] = getattr(
                    vgroups[vgroup].space, "total_used", None
                )
        if SAFE_MODE_VERSION in api_version:
            for vgroup in range(0, len(vgroups)):
                name = vgroups[vgroup].name
                vgroups_info[name]["priority_adjustment"] = vgroups[
                    vgroup
                ].priority_adjustment.priority_adjustment_operator + str(
                    vgroups[vgroup].priority_adjustment.priority_adjustment_value
                )
        if performance:
            vgs_performance = list(arrayv6.get_volume_groups_performance().items)
            for performance in range(0, len(vgs_performance)):
                vgroups_info[vgs_performance[performance].name]["performance"] = {
                    "bytes_per_mirrored_write": vgs_performance[
                        performance
                    ].bytes_per_mirrored_write,
                    "bytes_per_op": vgs_performance[performance].bytes_per_op,
                    "bytes_per_read": vgs_performance[performance].bytes_per_read,
                    "bytes_per_write": vgs_performance[performance].bytes_per_write,
                    "mirrored_write_bytes_per_sec": vgs_performance[
                        performance
                    ].mirrored_write_bytes_per_sec,
                    "mirrored_writes_per_sec": vgs_performance[
                        performance
                    ].mirrored_writes_per_sec,
                    "qos_rate_limit_usec_per_mirrored_write_op": vgs_performance[
                        performance
                    ].qos_rate_limit_usec_per_mirrored_write_op,
                    "qos_rate_limit_usec_per_read_op": vgs_performance[
                        performance
                    ].qos_rate_limit_usec_per_mirrored_write_op,
                    "qos_rate_limit_usec_per_write_op": vgs_performance[
                        performance
                    ].qos_rate_limit_usec_per_read_op,
                    "queue_usec_per_mirrored_write_op": vgs_performance[
                        performance
                    ].queue_usec_per_mirrored_write_op,
                    "queue_usec_per_read_op": vgs_performance[
                        performance
                    ].queue_usec_per_read_op,
                    "queue_usec_per_write_op": vgs_performance[
                        performance
                    ].queue_usec_per_write_op,
                    "read_bytes_per_sec": vgs_performance[
                        performance
                    ].read_bytes_per_sec,
                    "reads_per_sec": vgs_performance[performance].reads_per_sec,
                    "san_usec_per_mirrored_write_op": vgs_performance[
                        performance
                    ].san_usec_per_mirrored_write_op,
                    "san_usec_per_read_op": vgs_performance[
                        performance
                    ].san_usec_per_read_op,
                    "san_usec_per_write_op": vgs_performance[
                        performance
                    ].san_usec_per_write_op,
                    "service_usec_per_mirrored_write_op": vgs_performance[
                        performance
                    ].service_usec_per_mirrored_write_op,
                    "service_usec_per_read_op": vgs_performance[
                        performance
                    ].service_usec_per_read_op,
                    "service_usec_per_write_op": vgs_performance[
                        performance
                    ].service_usec_per_write_op,
                    "usec_per_mirrored_write_op": vgs_performance[
                        performance
                    ].usec_per_mirrored_write_op,
                    "usec_per_read_op": vgs_performance[performance].usec_per_read_op,
                    "usec_per_write_op": vgs_performance[performance].usec_per_write_op,
                    "write_bytes_per_sec": vgs_performance[
                        performance
                    ].write_bytes_per_sec,
                    "writes_per_sec": vgs_performance[performance].writes_per_sec,
                }
    return vgroups_info


def generate_del_vgroups_dict(module, array):
    vgroups_info = {}
    api_version = array._list_available_rest_versions()
    if AC_REQUIRED_API_VERSION in api_version:
        vgroups = array.list_vgroups(pending_only=True)
        for vgroup in range(0, len(vgroups)):
            virtgroup = vgroups[vgroup]["name"]
            vgroups_info[virtgroup] = {
                "volumes": vgroups[vgroup]["volumes"],
            }
    if V6_MINIMUM_API_VERSION in api_version:
        arrayv6 = get_array(module)
        vgroups = list(arrayv6.get_volume_groups(destroyed=True).items)
        for vgroup in range(0, len(vgroups)):
            name = vgroups[vgroup].name
            vgroups_info[name]["snapshots_space"] = vgroups[vgroup].space.snapshots
            # Provide system as this matches the old naming convention
            vgroups_info[name]["system"] = vgroups[vgroup].space.unique
            vgroups_info[name]["unique_space"] = vgroups[vgroup].space.unique
            vgroups_info[name]["virtual_space"] = vgroups[vgroup].space.virtual
            vgroups_info[name]["data_reduction"] = vgroups[vgroup].space.data_reduction
            vgroups_info[name]["total_reduction"] = vgroups[
                vgroup
            ].space.total_reduction
            vgroups_info[name]["total_provisioned"] = vgroups[
                vgroup
            ].space.total_provisioned
            vgroups_info[name]["thin_provisioning"] = vgroups[
                vgroup
            ].space.thin_provisioning
            vgroups_info[name]["used_provisioned"] = (
                getattr(vgroups[vgroup].space, "used_provisioned", None),
            )
            vgroups_info[name]["time_remaining"] = (vgroups[vgroup].time_remaining,)
            vgroups_info[name]["bandwidth_limit"] = getattr(
                vgroups[vgroup].qos, "bandwidth_limit", ""
            )
            vgroups_info[name]["iops_limit"] = getattr(
                vgroups[vgroup].qos, "iops_limit", ""
            )
        if SAFE_MODE_VERSION in api_version:
            for vgroup in range(0, len(vgroups)):
                name = vgroups[vgroup].name
                vgroups_info[name]["priority_adjustment"] = vgroups[
                    vgroup
                ].priority_adjustment.priority_adjustment_operator + str(
                    vgroups[vgroup].priority_adjustment.priority_adjustment_value
                )
    return vgroups_info


def generate_certs_dict(array):
    certs_info = {}
    api_version = array._list_available_rest_versions()
    if P53_API_VERSION in api_version:
        certs = array.list_certificates()
        for cert in range(0, len(certs)):
            certificate = certs[cert]["name"]
            valid_from = time.strftime(
                "%a, %d %b %Y %H:%M:%S %Z",
                time.localtime(certs[cert]["valid_from"] / 1000),
            )
            valid_to = time.strftime(
                "%a, %d %b %Y %H:%M:%S %Z",
                time.localtime(certs[cert]["valid_to"] / 1000),
            )
            certs_info[certificate] = {
                "status": certs[cert]["status"],
                "issued_to": certs[cert]["issued_to"],
                "valid_from": valid_from,
                "locality": certs[cert]["locality"],
                "country": certs[cert]["country"],
                "issued_by": certs[cert]["issued_by"],
                "valid_to": valid_to,
                "state": certs[cert]["state"],
                "key_size": certs[cert]["key_size"],
                "org_unit": certs[cert]["organizational_unit"],
                "common_name": certs[cert]["common_name"],
                "organization": certs[cert]["organization"],
                "email": certs[cert]["email"],
            }
    return certs_info


def generate_kmip_dict(array):
    kmip_info = {}
    kmips = list(array.get_kmip().items)
    for kmip in range(0, len(kmips)):
        key = kmips[kmip].name
        kmip_info[key] = {
            "certificate": kmips[kmip].certificate.name,
            "ca_certificate": getattr(kmips[kmip], "ca_certificate", None),
            "ca_cert_configured": True,
            "uri": kmips[kmip].uris,
        }
    return kmip_info


def generate_nfs_offload_dict(module, array):
    offload_info = {}
    api_version = array._list_available_rest_versions()
    if NSID_API_VERSION not in api_version:
        if AC_REQUIRED_API_VERSION in api_version:
            offload = array.list_nfs_offload()
            for target in range(0, len(offload)):
                offloadt = offload[target]["name"]
                offload_info[offloadt] = {
                    "status": offload[target]["status"],
                    "mount_point": offload[target]["mount_point"],
                    "protocol": offload[target]["protocol"],
                    "mount_options": offload[target]["mount_options"],
                    "address": offload[target]["address"],
                }
        if V6_MINIMUM_API_VERSION in api_version:
            arrayv6 = get_array(module)
            offloads = list(arrayv6.get_offloads(protocol="nfs").items)
            for offload in range(0, len(offloads)):
                name = offloads[offload].name
                offload_info[name]["snapshots"] = getattr(
                    offloads[offload].space, "snapshots", None
                )
                offload_info[name]["shared"] = getattr(
                    offloads[offload].space, "shared", None
                )
                offload_info[name]["data_reduction"] = getattr(
                    offloads[offload].space, "data_reduction", None
                )
                offload_info[name]["thin_provisioning"] = getattr(
                    offloads[offload].space, "thin_provisioning", None
                )
                offload_info[name]["total_physical"] = getattr(
                    offloads[offload].space, "total_physical", None
                )
                offload_info[name]["total_provisioned"] = getattr(
                    offloads[offload].space, "total_provisioned", None
                )
                offload_info[name]["total_reduction"] = getattr(
                    offloads[offload].space, "total_reduction", None
                )
                offload_info[name]["unique"] = getattr(
                    offloads[offload].space, "unique", None
                )
                offload_info[name]["virtual"] = getattr(
                    offloads[offload].space, "virtual", None
                )
                offload_info[name]["replication"] = getattr(
                    offloads[offload].space, "replication", None
                )
                offload_info[name]["used_provisioned"] = getattr(
                    offloads[offload].space, "used_provisioned", None
                )
                if SUBS_API_VERSION in api_version:
                    offload_info[name]["total_used"] = getattr(
                        offloads[offload].space, "total_used", None
                    )
    return offload_info


def generate_s3_offload_dict(module, array):
    offload_info = {}
    api_version = array._list_available_rest_versions()
    if S3_REQUIRED_API_VERSION in api_version:
        offload = array.list_s3_offload()
        for target in range(0, len(offload)):
            offloadt = offload[target]["name"]
            offload_info[offloadt] = {
                "status": offload[target]["status"],
                "bucket": offload[target]["bucket"],
                "protocol": offload[target]["protocol"],
                "access_key_id": offload[target]["access_key_id"],
            }
            if P53_API_VERSION in api_version:
                offload_info[offloadt]["placement_strategy"] = offload[target][
                    "placement_strategy"
                ]
    if V6_MINIMUM_API_VERSION in api_version:
        arrayv6 = get_array(module)
        offloads = list(arrayv6.get_offloads(protocol="s3").items)
        for offload in range(0, len(offloads)):
            name = offloads[offload].name
            offload_info[name]["snapshots"] = getattr(
                offloads[offload].space, "snapshots", None
            )
            offload_info[name]["shared"] = getattr(
                offloads[offload].space, "shared", None
            )
            offload_info[name]["data_reduction"] = getattr(
                offloads[offload].space, "data_reduction", None
            )
            offload_info[name]["thin_provisioning"] = getattr(
                offloads[offload].space, "thin_provisioning", None
            )
            offload_info[name]["total_physical"] = getattr(
                offloads[offload].space, "total_physical", None
            )
            offload_info[name]["total_provisioned"] = getattr(
                offloads[offload].space, "total_provisioned", None
            )
            offload_info[name]["total_reduction"] = getattr(
                offloads[offload].space, "total_reduction", None
            )
            offload_info[name]["unique"] = getattr(
                offloads[offload].space, "unique", None
            )
            offload_info[name]["virtual"] = getattr(
                offloads[offload].space, "virtual", None
            )
            offload_info[name]["replication"] = getattr(
                offloads[offload].space, "replication", None
            )
            offload_info[name]["used_provisioned"] = getattr(
                offloads[offload].space, "used_provisioned", None
            )
            if SUBS_API_VERSION in api_version:
                offload_info[name]["total_used"] = offloads[offload].space.total_used
    return offload_info


def generate_azure_offload_dict(module, array):
    offload_info = {}
    api_version = array._list_available_rest_versions()
    if P53_API_VERSION in api_version:
        offload = array.list_azure_offload()
        for target in range(0, len(offload)):
            offloadt = offload[target]["name"]
            offload_info[offloadt] = {
                "status": offload[target]["status"],
                "account_name": offload[target]["account_name"],
                "protocol": offload[target]["protocol"],
                "secret_access_key": offload[target]["secret_access_key"],
                "container_name": offload[target]["container_name"],
            }
    if V6_MINIMUM_API_VERSION in api_version:
        arrayv6 = get_array(module)
        offloads = list(arrayv6.get_offloads(protocol="azure").items)
        for offload in range(0, len(offloads)):
            name = offloads[offload].name
            offload_info[name]["snapshots"] = getattr(
                offloads[offload].space, "snapshots", None
            )
            offload_info[name]["shared"] = getattr(
                offloads[offload].space, "shared", None
            )
            offload_info[name]["data_reduction"] = getattr(
                offloads[offload].space, "data_reduction", None
            )
            offload_info[name]["thin_provisioning"] = getattr(
                offloads[offload].space, "thin_provisioning", None
            )
            offload_info[name]["total_physical"] = getattr(
                offloads[offload].space, "total_physical", None
            )
            offload_info[name]["total_provisioned"] = getattr(
                offloads[offload].space, "total_provisioned", None
            )
            offload_info[name]["total_reduction"] = getattr(
                offloads[offload].space, "total_reduction", None
            )
            offload_info[name]["unique"] = getattr(
                offloads[offload].space, "unique", None
            )
            offload_info[name]["virtual"] = getattr(
                offloads[offload].space, "virtual", None
            )
            offload_info[name]["replication"] = getattr(
                offloads[offload].space, "replication", None
            )
            offload_info[name]["used_provisioned"] = getattr(
                offloads[offload].space, "used_provisioned", None
            )
            if SUBS_API_VERSION in api_version:
                offload_info[name]["total_used"] = offloads[offload].space.total_used
    return offload_info


def generate_google_offload_dict(array):
    offload_info = {}
    offloads = list(array.get_offloads(protocol="google-cloud").items)
    for offload in range(0, len(offloads)):
        name = offloads[offload].name
        offload_info[name] = {
            # "access_key_id": offloads[offload].google-cloud.access_key_id,
            # "bucket": offloads[offload].google-cloud.bucket,
            # "auth_region": offloads[offload].google-cloud.auth_region,
            "snapshots": getattr(offloads[offload].space, "snapshots", None),
            "shared": getattr(offloads[offload].space, "shared", None),
            "data_reduction": getattr(offloads[offload].space, "data_reduction", None),
            "thin_provisioning": getattr(
                offloads[offload].space, "thin_provisioning", None
            ),
            "total_physical": getattr(offloads[offload].space, "total_physical", None),
            "total_provisioned": getattr(
                offloads[offload].space, "total_provisioned", None
            ),
            "total_reduction": getattr(
                offloads[offload].space, "total_reduction", None
            ),
            "unique": getattr(offloads[offload].space, "unique", None),
            "virtual": getattr(offloads[offload].space, "virtual", None),
            "replication": getattr(offloads[offload].space, "replication", None),
            "used_provisioned": getattr(
                offloads[offload].space, "used_provisioned", None
            ),
        }
        if LooseVersion(SUBS_API_VERSION) <= LooseVersion(array.get_rest_version()):
            offload_info[name]["total_used"] = offloads[offload].space.total_used
    return offload_info


def generate_hgroups_dict(module, array, performance):
    hgroups_info = {}
    api_version = array._list_available_rest_versions()
    hgroups = array.list_hgroups()
    for hgroup in range(0, len(hgroups)):
        hostgroup = hgroups[hgroup]["name"]
        hgroups_info[hostgroup] = {
            "hosts": hgroups[hgroup]["hosts"],
            "pgs": [],
            "vols": [],
        }
    pghgroups = array.list_hgroups(protect=True)
    for pghg in range(0, len(pghgroups)):
        pgname = pghgroups[pghg]["name"]
        hgroups_info[pgname]["pgs"].append(pghgroups[pghg]["protection_group"])
    volhgroups = array.list_hgroups(connect=True)
    for pgvol in range(0, len(volhgroups)):
        pgname = volhgroups[pgvol]["name"]
        volpgdict = [volhgroups[pgvol]["vol"], volhgroups[pgvol]["lun"]]
        hgroups_info[pgname]["vols"].append(volpgdict)
    if V6_MINIMUM_API_VERSION in api_version:
        arrayv6 = get_array(module)
        hgroups = list(arrayv6.get_host_groups().items)
        for hgroup in range(0, len(hgroups)):
            if hgroups[hgroup].is_local:
                name = hgroups[hgroup].name
                hgroups_info[name]["snapshots"] = getattr(
                    hgroups[hgroup].space, "snapshots", None
                )
                hgroups_info[name]["data_reduction"] = getattr(
                    hgroups[hgroup].space, "data_reduction", None
                )
                hgroups_info[name]["thin_provisioning"] = getattr(
                    hgroups[hgroup].space, "thin_provisioning", None
                )
                hgroups_info[name]["total_physical"] = getattr(
                    hgroups[hgroup].space, "total_physical", None
                )
                hgroups_info[name]["total_provisioned"] = getattr(
                    hgroups[hgroup].space, "total_provisioned", None
                )
                hgroups_info[name]["total_reduction"] = getattr(
                    hgroups[hgroup].space, "total_reduction", None
                )
                hgroups_info[name]["unique"] = getattr(
                    hgroups[hgroup].space, "unique", None
                )
                hgroups_info[name]["virtual"] = getattr(
                    hgroups[hgroup].space, "virtual", None
                )
                hgroups_info[name]["used_provisioned"] = getattr(
                    hgroups[hgroup].space, "used_provisioned", None
                )
                if SUBS_API_VERSION in api_version:
                    hgroups_info[name]["total_used"] = hgroups[hgroup].space.total_used
                if DSROLE_POLICY_API_VERSION in api_version:
                    hgroups_info[name]["destroyed"] = hgroups[hgroup].destroyed
                    if hgroups[hgroup].destroyed:
                        hgroups_info[name]["time_remaining"] = hgroups[
                            hgroup
                        ].time_remaining
        if performance:
            hgs_performance = list(arrayv6.get_host_groups_performance().items)
            for performance in range(0, len(hgs_performance)):
                if ":" not in hgs_performance[performance].name:
                    hgroups_info[hgs_performance[performance].name]["performance"] = {
                        "bytes_per_mirrored_write": hgs_performance[
                            performance
                        ].bytes_per_mirrored_write,
                        "bytes_per_op": hgs_performance[performance].bytes_per_op,
                        "bytes_per_read": hgs_performance[performance].bytes_per_read,
                        "bytes_per_write": hgs_performance[performance].bytes_per_write,
                        "mirrored_write_bytes_per_sec": hgs_performance[
                            performance
                        ].mirrored_write_bytes_per_sec,
                        "mirrored_writes_per_sec": hgs_performance[
                            performance
                        ].mirrored_writes_per_sec,
                        "qos_rate_limit_usec_per_mirrored_write_op": hgs_performance[
                            performance
                        ].qos_rate_limit_usec_per_mirrored_write_op,
                        "qos_rate_limit_usec_per_read_op": hgs_performance[
                            performance
                        ].qos_rate_limit_usec_per_mirrored_write_op,
                        "qos_rate_limit_usec_per_write_op": hgs_performance[
                            performance
                        ].qos_rate_limit_usec_per_read_op,
                        "queue_usec_per_mirrored_write_op": hgs_performance[
                            performance
                        ].queue_usec_per_mirrored_write_op,
                        "queue_usec_per_read_op": hgs_performance[
                            performance
                        ].queue_usec_per_read_op,
                        "queue_usec_per_write_op": hgs_performance[
                            performance
                        ].queue_usec_per_write_op,
                        "read_bytes_per_sec": hgs_performance[
                            performance
                        ].read_bytes_per_sec,
                        "reads_per_sec": hgs_performance[performance].reads_per_sec,
                        "san_usec_per_mirrored_write_op": hgs_performance[
                            performance
                        ].san_usec_per_mirrored_write_op,
                        "san_usec_per_read_op": hgs_performance[
                            performance
                        ].san_usec_per_read_op,
                        "san_usec_per_write_op": hgs_performance[
                            performance
                        ].san_usec_per_write_op,
                        "service_usec_per_mirrored_write_op": hgs_performance[
                            performance
                        ].service_usec_per_mirrored_write_op,
                        "service_usec_per_read_op": hgs_performance[
                            performance
                        ].service_usec_per_read_op,
                        "service_usec_per_write_op": hgs_performance[
                            performance
                        ].service_usec_per_write_op,
                        "usec_per_mirrored_write_op": hgs_performance[
                            performance
                        ].usec_per_mirrored_write_op,
                        "usec_per_read_op": hgs_performance[
                            performance
                        ].usec_per_read_op,
                        "usec_per_write_op": hgs_performance[
                            performance
                        ].usec_per_write_op,
                        "write_bytes_per_sec": hgs_performance[
                            performance
                        ].write_bytes_per_sec,
                        "writes_per_sec": hgs_performance[performance].writes_per_sec,
                    }
    return hgroups_info


def generate_interfaces_dict(array):
    api_version = array._list_available_rest_versions()
    int_info = {}
    ports = array.list_ports()
    for port in range(0, len(ports)):
        int_name = ports[port]["name"]
        if ports[port]["wwn"]:
            int_info[int_name] = ports[port]["wwn"]
        if ports[port]["iqn"]:
            int_info[int_name] = ports[port]["iqn"]
        if NVME_API_VERSION in api_version:
            if ports[port]["nqn"]:
                int_info[int_name] = ports[port]["nqn"]
    return int_info


def generate_vm_dict(array):
    vm_info = {}
    virt_machines = list(array.get_virtual_machines(vm_type="vvol").items)
    for machine in range(0, len(virt_machines)):
        name = virt_machines[machine].name
        vm_info[name] = {
            "vm_type": virt_machines[machine].vm_type,
            "vm_id": virt_machines[machine].vm_id,
            "destroyed": virt_machines[machine].destroyed,
            "created": virt_machines[machine].created,
            "time_remaining": getattr(virt_machines[machine], "time_remaining", None),
            "latest_snapshot_name": getattr(
                virt_machines[machine].recover_context, "name", None
            ),
            "latest_snapshot_id": getattr(
                virt_machines[machine].recover_context, "id", None
            ),
        }
    return vm_info


def generate_alerts_dict(array):
    alerts_info = {}
    alerts = list(array.get_alerts().items)
    for alert in range(0, len(alerts)):
        name = alerts[alert].name
        try:
            notified_time = alerts[alert].notified / 1000
            notified_datetime = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(notified_time)
            )
        except AttributeError:
            notified_datetime = ""
        try:
            closed_time = alerts[alert].closed / 1000
            closed_datetime = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(closed_time)
            )
        except AttributeError:
            closed_datetime = ""
        try:
            updated_time = alerts[alert].updated / 1000
            updated_datetime = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(updated_time)
            )
        except AttributeError:
            updated_datetime = ""
        try:
            created_time = alerts[alert].created / 1000
            created_datetime = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(created_time)
            )
        except AttributeError:
            updated_datetime = ""
        alerts_info[name] = {
            "flagged": alerts[alert].flagged,
            "category": alerts[alert].category,
            "code": alerts[alert].code,
            "issue": alerts[alert].issue,
            "kb_url": alerts[alert].knowledge_base_url,
            "summary": alerts[alert].summary,
            "id": alerts[alert].id,
            "state": alerts[alert].state,
            "severity": alerts[alert].severity,
            "component_name": alerts[alert].component_name,
            "component_type": alerts[alert].component_type,
            "created": created_datetime,
            "closed": closed_datetime,
            "notified": notified_datetime,
            "updated": updated_datetime,
            "actual": getattr(alerts[alert], "actual", ""),
            "expected": getattr(alerts[alert], "expected", ""),
        }
    return alerts_info


def generate_vmsnap_dict(array):
    vmsnap_info = {}
    virt_snaps = list(array.get_virtual_machine_snapshots(vm_type="vvol").items)
    for snap in range(0, len(virt_snaps)):
        name = virt_snaps[snap].name
        vmsnap_info[name] = {
            "vm_type": virt_snaps[snap].vm_type,
            "vm_id": virt_snaps[snap].vm_id,
            "destroyed": virt_snaps[snap].destroyed,
            "created": virt_snaps[snap].created,
            "time_remaining": getattr(virt_snaps[snap], "time_remaining", None),
            "latest_pgsnapshot_name": getattr(
                virt_snaps[snap].recover_context, "name", None
            ),
            "latest_pgsnapshot_id": getattr(
                virt_snaps[snap].recover_context, "id", None
            ),
        }
    return vmsnap_info


def generate_subs_dict(array):
    subs_info = {}
    subs = list(array.get_subscription_assets().items)
    for sub in range(0, len(subs)):
        name = subs[sub].name
        subs_info[name] = {
            "subscription_id": subs[sub].subscription.id,
        }
    return subs_info


def generate_fleet_dict(array):
    fleet_info = {}
    fleet = list(array.get_fleets().items)
    if fleet:
        fleet_name = list(array.get_fleets().items)[0].name
        fleet_info[fleet_name] = {
            "members": {},
        }
        members = list(array.get_fleets_members().items)
        for member in range(0, len(members)):
            name = members[member].member.name
            fleet_info[fleet_name]["members"][name] = {
                "status": members[member].status,
                "status_details": members[member].status_details,
            }
    return fleet_info


def generate_realms_dict(array, performance):
    realms_info = {}
    realms = list(array.get_realms().items)
    for realm in range(0, len(realms)):
        name = realms[realm].name
        realms_info[name] = {
            "created": time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(realms[realm].created / 1000)
            ),
            "destroyed": realms[realm].destroyed,
            "quota_limit": realms[realm].quota_limit,
            "data_reduction": getattr(realms[realm].space, "data_reduction", None),
            "footprint": getattr(realms[realm].space, "footprint", None),
            "shared": getattr(realms[realm].space, "shared", None),
            "snapshots": getattr(realms[realm].space, "snapshots", None),
            "thin_provisioning": getattr(
                realms[realm].space, "thin_provisioning", None
            ),
            "total_provisioned": getattr(
                realms[realm].space, "total_provisioned", None
            ),
            "total_reduction": getattr(realms[realm].space, "total_reduction", None),
            "total_used": getattr(realms[realm].space, "total_used", None),
            "unique": getattr(realms[realm].space, "unique", None),
            "used_provisioned": getattr(realms[realm].space, "used_provisioned", None),
            "virtual": getattr(realms[realm].space, "virtual", None),
            "performance": [],
            "qos": [],
        }
        realms_info[name]["qos"] = {
            "iops_limit": getattr(realms[realm].qos, "iops_limit", None),
            "bandwidth_limit": getattr(realms[realm].qos, "bandwidth_limit", None),
        }
        if realms_info[name]["destroyed"]:
            realms_info[name]["time_remaining"] = realms[realm].time_remaining
    if performance:
        r_perfs = list(array.get_realms_performance().items)
        for performance in range(0, len(r_perfs)):
            realms_info[r_perfs[performance].name]["performance"] = {
                "bytes_per_mirrored_write": r_perfs[
                    performance
                ].bytes_per_mirrored_write,
                "bytes_per_op": r_perfs[performance].bytes_per_op,
                "bytes_per_read": r_perfs[performance].bytes_per_read,
                "bytes_per_write": r_perfs[performance].bytes_per_write,
                "mirrored_write_bytes_per_sec": r_perfs[
                    performance
                ].mirrored_write_bytes_per_sec,
                "mirrored_writes_per_sec": r_perfs[performance].mirrored_writes_per_sec,
                "others_per_sec": r_perfs[performance].others_per_sec,
                "qos_rate_limit_usec_per_mirrored_write_op": r_perfs[
                    performance
                ].qos_rate_limit_usec_per_mirrored_write_op,
                "qos_rate_limit_usec_per_read_op": r_perfs[
                    performance
                ].qos_rate_limit_usec_per_mirrored_write_op,
                "qos_rate_limit_usec_per_write_op": r_perfs[
                    performance
                ].qos_rate_limit_usec_per_read_op,
                "queue_usec_per_mirrored_write_op": r_perfs[
                    performance
                ].queue_usec_per_mirrored_write_op,
                "queue_usec_per_read_op": r_perfs[performance].queue_usec_per_read_op,
                "queue_usec_per_write_op": r_perfs[performance].queue_usec_per_write_op,
                "read_bytes_per_sec": r_perfs[performance].read_bytes_per_sec,
                "reads_per_sec": r_perfs[performance].reads_per_sec,
                "san_usec_per_mirrored_write_op": r_perfs[
                    performance
                ].san_usec_per_mirrored_write_op,
                "san_usec_per_read_op": r_perfs[performance].san_usec_per_read_op,
                "san_usec_per_write_op": r_perfs[performance].san_usec_per_write_op,
                "service_usec_per_mirrored_write_op": r_perfs[
                    performance
                ].service_usec_per_mirrored_write_op,
                "service_usec_per_read_op": r_perfs[
                    performance
                ].service_usec_per_read_op,
                "service_usec_per_write_op": r_perfs[
                    performance
                ].service_usec_per_write_op,
                "usec_per_mirrored_write_op": r_perfs[
                    performance
                ].usec_per_mirrored_write_op,
                "usec_per_other_op": r_perfs[performance].usec_per_other_op,
                "usec_per_read_op": r_perfs[performance].usec_per_read_op,
                "usec_per_write_op": r_perfs[performance].usec_per_write_op,
                "write_bytes_per_sec": r_perfs[performance].write_bytes_per_sec,
                "writes_per_sec": r_perfs[performance].writes_per_sec,
            }
    return realms_info


def main():
    argument_spec = purefa_argument_spec()
    argument_spec.update(
        dict(gather_subset=dict(default="minimum", type="list", elements="str"))
    )

    module = AnsibleModule(argument_spec, supports_check_mode=True)
    array = get_system(module)
    api_version = array._list_available_rest_versions()

    subset = [test.lower() for test in module.params["gather_subset"]]
    valid_subsets = (
        "all",
        "minimum",
        "config",
        "performance",
        "capacity",
        "network",
        "subnet",
        "interfaces",
        "hgroups",
        "pgroups",
        "hosts",
        "admins",
        "volumes",
        "snapshots",
        "pods",
        "replication",
        "vgroups",
        "offload",
        "apps",
        "arrays",
        "certs",
        "kmip",
        "clients",
        "policies",
        "dir_snaps",
        "filesystems",
        "alerts",
        "virtual_machines",
        "subscriptions",
        "realms",
        "fleet",
    )
    subset_test = (test in valid_subsets for test in subset)
    if not all(subset_test):
        module.fail_json(
            msg="value must gather_subset must be one or more of: %s, got: %s"
            % (",".join(valid_subsets), ",".join(subset))
        )

    info = {}
    performance = False
    if "minimum" in subset or "all" in subset or "apps" in subset:
        info["default"] = generate_default_dict(module, array)
    if "performance" in subset or "all" in subset:
        performance = True
        info["performance"] = generate_perf_dict(array)
    if "config" in subset or "all" in subset:
        info["config"] = generate_config_dict(module, array)
    if "capacity" in subset or "all" in subset:
        info["capacity"] = generate_capacity_dict(module, array)
    if "network" in subset or "all" in subset:
        info["network"] = generate_network_dict(module, array, performance)
    if "subnet" in subset or "all" in subset:
        info["subnet"] = generate_subnet_dict(array)
    if "interfaces" in subset or "all" in subset:
        info["interfaces"] = generate_interfaces_dict(array)
    if "hosts" in subset or "all" in subset:
        info["hosts"] = generate_host_dict(module, array, performance)
    if "volumes" in subset or "all" in subset:
        info["volumes"] = generate_vol_dict(module, array, performance)
        info["deleted_volumes"] = generate_del_vol_dict(module, array)
    if "snapshots" in subset or "all" in subset:
        info["snapshots"] = generate_snap_dict(module, array)
        info["deleted_snapshots"] = generate_del_snap_dict(module, array)
    if "hgroups" in subset or "all" in subset:
        info["hgroups"] = generate_hgroups_dict(module, array, performance)
    if "pgroups" in subset or "all" in subset:
        info["pgroups"] = generate_pgroups_dict(module, array)
        info["deleted_pgroups"] = generate_del_pgroups_dict(module, array)
    if "pods" in subset or "all" in subset or "replication" in subset:
        info["replica_links"] = generate_rl_dict(module, array)
        info["pods"] = generate_pods_dict(module, array, performance)
        info["deleted_pods"] = generate_del_pods_dict(module, array)
    if "admins" in subset or "all" in subset:
        info["admins"] = generate_admin_dict(array)
    if "vgroups" in subset or "all" in subset:
        info["vgroups"] = generate_vgroups_dict(module, array, performance)
        info["deleted_vgroups"] = generate_del_vgroups_dict(module, array)
    if "offload" in subset or "all" in subset:
        info["azure_offload"] = generate_azure_offload_dict(module, array)
        info["nfs_offload"] = generate_nfs_offload_dict(module, array)
        info["s3_offload"] = generate_s3_offload_dict(module, array)
    if "apps" in subset or "all" in subset:
        if "CBS" not in info["default"]["array_model"]:
            info["apps"] = generate_apps_dict(array)
        else:
            info["apps"] = {}
    if "arrays" in subset or "all" in subset:
        info["arrays"] = generate_conn_array_dict(module, array)
    if "certs" in subset or "all" in subset:
        info["certs"] = generate_certs_dict(array)
    if FILES_API_VERSION in api_version:
        array_v6 = get_array(module)
        if "kmip" in subset or "all" in subset:
            info["kmip"] = generate_kmip_dict(array_v6)
        if "offload" in subset or "all" in subset:
            info["google_offload"] = generate_google_offload_dict(array_v6)
        if "filesystems" in subset or "all" in subset:
            info["filesystems"] = generate_filesystems_dict(array_v6)
        if "policies" in subset or "all" in subset:
            if NFS_USER_MAP_VERSION in api_version:
                user_map = True
            else:
                user_map = False
            if DIR_QUOTA_API_VERSION in api_version:
                quota = True
            else:
                quota = False
            if AUTODIR_API_VERSION in api_version:
                autodir = True
            else:
                autodir = False
            info["policies"] = generate_policies_dict(
                array_v6, quota, autodir, user_map
            )
        if "clients" in subset or "all" in subset:
            info["clients"] = generate_clients_dict(array_v6)
        if "dir_snaps" in subset or "all" in subset:
            info["dir_snaps"] = generate_dir_snaps_dict(array_v6)
        if "snapshots" in subset or "all" in subset:
            info["pg_snapshots"] = generate_pgsnaps_dict(array_v6)
        if "alerts" in subset or "all" in subset:
            info["alerts"] = generate_alerts_dict(array_v6)
        if SUBS_API_VERSION in api_version and (
            "subscriptions" in subset or "all" in subset
        ):
            info["subscriptions"] = generate_subs_dict(array_v6)
        if VM_VERSION in api_version and (
            "virtual_machines" in subset or "all" in subset
        ):
            info["virtual_machines"] = generate_vm_dict(array_v6)
            info["virtual_machines_snaps"] = generate_vmsnap_dict(array_v6)
        if DSROLE_POLICY_API_VERSION in api_version:
            if "realms" in subset or "all" in subset:
                info["realms"] = generate_realms_dict(array_v6, performance)
        if CONTEXT_API_VERSION in api_version:
            if "fleet" in subset or "all" in subset:
                info["fleet"] = generate_fleet_dict(array_v6)
    module.exit_json(changed=False, purefa_info=info)


if __name__ == "__main__":
    main()
