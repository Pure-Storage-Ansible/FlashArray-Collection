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
module: purefa_info
version_added: '2.9'
short_description: Collect information from Pure Storage FlashArray
description:
  - Collect information from a Pure Storage Flasharray running the
    Purity//FA operating system. By default, the module will collect basic
    information including hosts, host groups, protection
    groups and volume counts. Additional information can be collected
    based on the configured set of arguements.
author:
  - Pure Storage ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
options:
  gather_subset:
    description:
      - When supplied, this argument will define the information to be collected.
        Possible values for this include all, minimum, config, performance,
        capacity, network, subnet, interfaces, hgroups, pgroups, hosts,
        admins, volumes, snapshots, pods, replication, vgroups, offload, apps,
        arrays, certs and kmip.
    type: list
    required: false
    default: minimum
extends_documentation_fragment:
  - purestorage.flasharray.purestorage.fa
'''

EXAMPLES = r'''
- name: collect default set of information
  purefa_info:
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
  register: array_info
- name: show default information
  debug:
    msg: "{{ array_info['purefa_info']['default'] }}"

- name: collect configuration and capacity information
  purefa_info:
    gather_subset:
      - config
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
  register: array_info
- name: show configuration information
  debug:
    msg: "{{ array_info['purefa_info']['config'] }}"

- name: collect all information
  purefa_info:
    gather_subset:
      - all
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592
- name: show all information
  debug:
    msg: "{{ array_info['purefa_info'] }}"
'''

RETURN = r'''
purefa_info:
  description: Returns the information collected from the FlashArray
  returned: always
  type: complex
  sample: {
        "admins": {
            "pureuser": {
                "role": "array_admin",
                "type": "local"
            }
        },
        "apps": {
            "offload": {
                "description": "Snapshot offload to NFS or Amazon S3",
                "status": "healthy",
                "version": "5.2.1"
            }
        },
        "arrays": {},
        "capacity": {
            "data_reduction": 11.664774599686346,
            "free_space": 6995782867042,
            "provisioned_space": 442391871488,
            "shared_space": 3070918120,
            "snapshot_space": 284597118,
            "system_space": 0,
            "thin_provisioning": 0.8201773449669771,
            "total_capacity": 7002920315199,
            "total_reduction": 64.86821472825108,
            "volume_space": 3781932919
        },
        "config": {
            "directory_service": {
                "base_dn": null,
                "bind_password": null,
                "bind_user": null,
                "check_peer": false,
                "enabled": false,
                "uri": [],
                "user_login_attribute": null,
                "user_object_class": null
            },
            "directory_service_roles": {
                "array_admin": {
                    "group": null,
                    "group_base": null
                },
                "ops_admin": {
                    "group": null,
                    "group_base": null
                },
                "readonly": {
                    "group": null,
                    "group_base": null
                },
                "storage_admin": {
                    "group": null,
                    "group_base": null
                }
            },
            "dns": {
                "domain": "acme.com",
                "nameservers": [
                    "8.8.4.4"
                ]
            },
            "global_admin": {
                "lockout_duration": null,
                "max_login_attempts": null,
                "min_password_length": 1,
                "single_sign_on_enabled": false
            },
            "idle_timeout": 0,
            "ntp": [
                "prod-ntp1.puretec.purestorage.com"
            ],
            "phonehome": "enabled",
            "proxy": "",
            "relayhost": "smtp.puretec.purestorage.com",
            "scsi_timeout": 60,
            "senderdomain": "purestorage.com",
            "smtp": [
                {
                    "enabled": true,
                    "name": "flasharray-alerts@purestorage.com"
                }
            ],
            "snmp": [
                {
                    "auth_passphrase": null,
                    "auth_protocol": null,
                    "community": "",
                    "host": "10.21.23.34",
                    "name": "manager1",
                    "notification": "trap",
                    "privacy_passphrase": null,
                    "privacy_protocol": null,
                    "user": null,
                    "version": "v2c"
                }
            ],
            "syslog": [
                "udp://prod-ntp2.puretec.purestorage.com:333"
            ]
        },
        "default": {
            "admins": 1,
            "array_model": "FA-405",
            "array_name": "array",
            "connected_arrays": 0,
            "connection_key": "c6033033-fe69-2515-a9e8-966bb7fe4b40",
            "hostgroups": 0,
            "hosts": 15,
            "pods": 1,
            "protection_groups": 1,
            "purity_version": "5.2.1",
            "snapshots": 2,
            "volume_groups": 1
        },
        "hgroups": {},
        "hosts": {
            "@offload": {
                "hgroup": null,
                "iqn": [],
                "nqn": [],
                "personality": null,
                "preferred_array": [],
                "target_port": [],
                "wwn": []
            },
            "docker-host": {
                "hgroup": null,
                "iqn": [
                    "iqn.1994-05.com.redhat:d97adf78472"
                ],
                "nqn": [],
                "personality": null,
                "preferred_array": [],
                "target_port": [
                    "CT0.ETH4",
                    "CT1.ETH4"
                ],
                "wwn": []
            }
        },
        "interfaces": {
            "CT0.ETH4": "iqn.2010-06.com.purestorage:flasharray.2111b767484e4682",
            "CT1.ETH4": "iqn.2010-06.com.purestorage:flasharray.2111b767484e4682",
        },
        "network": {
            "@offload.data0": {
                "address": "10.21.200.222",
                "gateway": "10.21.200.1",
                "hwaddr": "52:54:30:02:b9:4e",
                "mtu": 1500,
                "netmask": "255.255.255.0",
                "services": [
                    "app"
                ],
                "speed": 10000000000
            },
            "ct0.eth0": {
                "address": "10.21.200.211",
                "gateway": "10.21.200.1",
                "hwaddr": "ec:f4:bb:c8:8a:04",
                "mtu": 1500,
                "netmask": "255.255.255.0",
                "services": [
                    "management"
                ],
                "speed": 1000000000
            },
            "ct0.eth2": {
                "address": "10.21.200.218",
                "gateway": null,
                "hwaddr": "ec:f4:bb:c8:8a:00",
                "mtu": 1500,
                "netmask": "255.255.255.0",
                "services": [
                    "replication"
                ],
                "speed": 10000000000
            },
            "ct0.eth4": {
                "address": "10.21.200.214",
                "gateway": null,
                "hwaddr": "90:e2:ba:83:79:0c",
                "mtu": 1500,
                "netmask": "255.255.255.0",
                "services": [
                    "iscsi"
                ],
                "speed": 10000000000
            },
            "ct1.eth0": {
                "address": "10.21.200.212",
                "gateway": "10.21.200.1",
                "hwaddr": "ec:f4:bb:e4:c6:3c",
                "mtu": 1500,
                "netmask": "255.255.255.0",
                "services": [
                    "management"
                ],
                "speed": 1000000000
            },
            "ct1.eth2": {
                "address": "10.21.200.220",
                "gateway": null,
                "hwaddr": "ec:f4:bb:e4:c6:38",
                "mtu": 1500,
                "netmask": "255.255.255.0",
                "services": [
                    "replication"
                ],
                "speed": 10000000000
            },
            "ct1.eth4": {
                "address": "10.21.200.216",
                "gateway": null,
                "hwaddr": "90:e2:ba:8b:b1:8c",
                "mtu": 1500,
                "netmask": "255.255.255.0",
                "services": [
                    "iscsi"
                ],
                "speed": 10000000000
            },
            "vir0": {
                "address": "10.21.200.210",
                "gateway": "10.21.200.1",
                "hwaddr": "fe:ba:e9:e7:6b:0f",
                "mtu": 1500,
                "netmask": "255.255.255.0",
                "services": [
                    "management"
                ],
                "speed": 1000000000
            }
        },
        "nfs_offload": {},
        "performance": {
            "input_per_sec": 0,
            "local_queue_usec_per_op": 0,
            "output_per_sec": 0,
            "qos_rate_limit_usec_per_read_op": 0,
            "qos_rate_limit_usec_per_write_op": 0,
            "queue_depth": 0,
            "queue_usec_per_read_op": 0,
            "queue_usec_per_write_op": 0,
            "reads_per_sec": 0,
            "san_usec_per_read_op": 0,
            "san_usec_per_write_op": 0,
            "time": "2019-08-14T21:33:51Z",
            "usec_per_read_op": 0,
            "usec_per_write_op": 0,
            "writes_per_sec": 0
        },
        "pgroups": {
            "test_pg": {
                "hgroups": null,
                "hosts": null,
                "source": "docker-host",
                "targets": null,
                "volumes": null
            }
        },
        "pods": {
            "test": {
                "arrays": [
                    {
                        "array_id": "043be47c-1233-4399-b9d6-8fe38727dd9d",
                        "mediator_status": "online",
                        "name": "array2",
                        "status": "online"
                    }
                ],
                "source": null
            }
        },
        "s3_offload": {
            "s3-offload": {
                "access_key_id": "AKIAILNVEPWZTV4FGWZQ",
                "bucket": "offload-bucket",
                "protocol": "s3",
                "status": "connected"
            }
        },
        "snapshots": {
            "@offload_boot.1": {
                "created": "2019-03-14T15:29:20Z",
                "size": 68719476736,
                "source": "@offload_boot"
            }
        },
        "subnet": {},
        "vgroups": {
            "test": {
                "volumes": [
                    "test/test",
                    "test/test1"
                ]
            }
        },
        "volumes": {
            "@offload_boot": {
                "bandwidth": null,
                "hosts": [
                    [
                        "@offload",
                        1
                    ]
                ],
                "serial": "43BE47C12334399B00013959",
                "size": 68719476736,
                "source": null
            },
            "docker-store": {
                "bandwidth": null,
                "hosts": [
                    [
                        "docker-host",
                        1
                    ]
                ],
                "serial": "43BE47C12334399B00011418",
                "size": 21474836480,
                "source": null
            }
        }
    }
'''


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.flasharray.plugins.module_utils.purefa import get_array, get_system, purefa_argument_spec
import time

ADMIN_API_VERSION = '1.14'
S3_REQUIRED_API_VERSION = '1.16'
LATENCY_REQUIRED_API_VERSION = '1.16'
AC_REQUIRED_API_VERSION = '1.14'
CAP_REQUIRED_API_VERSION = '1.6'
SAN_REQUIRED_API_VERSION = '1.10'
NVME_API_VERSION = '1.16'
PREFERRED_API_VERSION = '1.15'
P53_API_VERSION = '1.17'
ACTIVE_DR_API = '1.19'
V6_MINIMUM_API_VERSION = '2.2'


def generate_default_dict(array):
    default_info = {}
    defaults = array.get()
    api_version = array._list_available_rest_versions()
    if AC_REQUIRED_API_VERSION in api_version:
        default_info['volume_groups'] = len(array.list_vgroups())
        default_info['connected_arrays'] = len(array.list_array_connections())
        default_info['pods'] = len(array.list_pods())
        default_info['connection_key'] = array.get(connection_key=True)['connection_key']
    hosts = array.list_hosts()
    admins = array.list_admins()
    snaps = array.list_volumes(snap=True, pending=True)
    pgroups = array.list_pgroups(pending=True)
    hgroups = array.list_hgroups()
    default_info['array_model'] = array.get(controllers=True)[0]['model']
    default_info['array_name'] = defaults['array_name']
    default_info['purity_version'] = defaults['version']
    default_info['hosts'] = len(hosts)
    default_info['snapshots'] = len(snaps)
    default_info['protection_groups'] = len(pgroups)
    default_info['hostgroups'] = len(hgroups)
    default_info['admins'] = len(admins)
    default_info['remote_assist'] = array.get_remote_assist_status()['status']
    if P53_API_VERSION in api_version:
        default_info['maintenance_window'] = array.list_maintenance_windows()
    return default_info


def generate_perf_dict(array):
    perf_info = {}
    api_version = array._list_available_rest_versions()
    if LATENCY_REQUIRED_API_VERSION in api_version:
        latency_info = array.get(action='monitor', latency=True)[0]
    perf_info = array.get(action='monitor')[0]
    perf_info['writes_per_sec'] = perf_info['writes_per_sec']
    perf_info['reads_per_sec'] = perf_info['reads_per_sec']

    perf_info['input_per_sec'] = perf_info['input_per_sec']
    perf_info['output_per_sec'] = perf_info['output_per_sec']

    if LATENCY_REQUIRED_API_VERSION in api_version:
        perf_info['san_usec_per_read_op'] = latency_info['san_usec_per_read_op']
        perf_info['san_usec_per_write_op'] = latency_info['san_usec_per_write_op']
        perf_info['queue_usec_per_read_op'] = latency_info['queue_usec_per_read_op']
        perf_info['queue_usec_per_write_op'] = latency_info['queue_usec_per_write_op']
        perf_info['qos_rate_limit_usec_per_read_op'] = latency_info['qos_rate_limit_usec_per_read_op']
        perf_info['qos_rate_limit_usec_per_write_op'] = latency_info['qos_rate_limit_usec_per_write_op']
        perf_info['local_queue_usec_per_op'] = perf_info['local_queue_usec_per_op']
    perf_info['usec_per_read_op'] = perf_info['usec_per_read_op']
    perf_info['usec_per_write_op'] = perf_info['usec_per_write_op']
    perf_info['queue_depth'] = perf_info['queue_depth']
    return perf_info


def generate_config_dict(module, array):
    config_info = {}
    api_version = array._list_available_rest_versions()
    config_info['console_lock'] = array.get_console_lock_status()['console_lock']
    config_info['dns'] = array.get_dns()
    config_info['smtp'] = array.list_alert_recipients()
    config_info['snmp'] = array.list_snmp_managers()
    config_info['snmp_v3_engine_id'] = array.get_snmp_engine_id()['engine_id']
    try:
        config_info['directory_service'] = array.get_directory_service()
    except Exception:
        config_info['directory_service'] = ['Array and Data Configurations found']
    if S3_REQUIRED_API_VERSION in api_version:
        config_info['directory_service_roles'] = {}
        roles = array.list_directory_service_roles()
        for role in range(0, len(roles)):
            role_name = roles[role]['name']
            config_info['directory_service_roles'][role_name] = {
                'group': roles[role]['group'],
                'group_base': roles[role]['group_base'],
            }
    else:
        config_info['directory_service'].update(array.get_directory_service(groups=True))
    config_info['ntp'] = array.get(ntpserver=True)['ntpserver']
    config_info['syslog'] = array.get(syslogserver=True)['syslogserver']
    config_info['phonehome'] = array.get(phonehome=True)['phonehome']
    config_info['proxy'] = array.get(proxy=True)['proxy']
    config_info['relayhost'] = array.get(relayhost=True)['relayhost']
    config_info['senderdomain'] = array.get(senderdomain=True)['senderdomain']
    config_info['syslog'] = array.get(syslogserver=True)['syslogserver']
    config_info['idle_timeout'] = array.get(idle_timeout=True)['idle_timeout']
    config_info['scsi_timeout'] = array.get(scsi_timeout=True)['scsi_timeout']
    if S3_REQUIRED_API_VERSION in api_version:
        config_info['global_admin'] = array.get_global_admin_attributes()
    if V6_MINIMUM_API_VERSION in api_version:
        array = get_array(module)
        smi_s = list(array.get_smi_s().items)[0]
        config_info['smi-s'] = {
            'slp_enabled': smi_s.slp_enabled,
            'wbem_https_enabled': smi_s.wbem_https_enabled
        }
    return config_info


def generate_admin_dict(array):
    admin_info = {}
    api_version = array._list_available_rest_versions()
    if ADMIN_API_VERSION in api_version:
        admins = array.list_admins()
        for admin in range(0, len(admins)):
            admin_name = admins[admin]['name']
            admin_info[admin_name] = {
                'type': admins[admin]['type'],
                'role': admins[admin]['role'],
            }
    return admin_info


def generate_subnet_dict(array):
    sub_info = {}
    subnets = array.list_subnets()
    for sub in range(0, len(subnets)):
        sub_name = subnets[sub]['name']
        if subnets[sub]['enabled']:
            sub_info[sub_name] = {
                'gateway': subnets[sub]['gateway'],
                'mtu': subnets[sub]['mtu'],
                'vlan': subnets[sub]['vlan'],
                'prefix': subnets[sub]['prefix'],
                'interfaces': subnets[sub]['interfaces'],
                'services': subnets[sub]['services'],
            }
    return sub_info


def generate_network_dict(array):
    net_info = {}
    ports = array.list_network_interfaces()
    for port in range(0, len(ports)):
        int_name = ports[port]['name']
        net_info[int_name] = {
            'hwaddr': ports[port]['hwaddr'],
            'mtu': ports[port]['mtu'],
            'enabled': ports[port]['enabled'],
            'speed': ports[port]['speed'],
            'address': ports[port]['address'],
            'slaves': ports[port]['slaves'],
            'services': ports[port]['services'],
            'gateway': ports[port]['gateway'],
            'netmask': ports[port]['netmask'],
        }
        if ports[port]['subnet']:
            subnets = array.get_subnet(ports[port]['subnet'])
            if subnets['enabled']:
                net_info[int_name]['subnet'] = {
                    'name': subnets['name'],
                    'prefix': subnets['prefix'],
                    'vlan': subnets['vlan'],
                }
    return net_info


def generate_capacity_dict(array):
    capacity_info = {}
    api_version = array._list_available_rest_versions()
    if CAP_REQUIRED_API_VERSION in api_version:
        volumes = array.list_volumes(pending=True)
        capacity_info['provisioned_space'] = sum(item['size'] for item in volumes)
        capacity = array.get(space=True)
        total_capacity = capacity[0]['capacity']
        used_space = capacity[0]["total"]
        capacity_info['free_space'] = total_capacity - used_space
        capacity_info['total_capacity'] = total_capacity
        capacity_info['data_reduction'] = capacity[0]['data_reduction']
        capacity_info['system_space'] = capacity[0]['system']
        capacity_info['volume_space'] = capacity[0]['volumes']
        capacity_info['shared_space'] = capacity[0]['shared_space']
        capacity_info['snapshot_space'] = capacity[0]['snapshots']
        capacity_info['thin_provisioning'] = capacity[0]['thin_provisioning']
        capacity_info['total_reduction'] = capacity[0]['total_reduction']
    return capacity_info


def generate_snap_dict(array):
    snap_info = {}
    api_version = array._list_available_rest_versions()
    snaps = array.list_volumes(snap=True)
    for snap in range(0, len(snaps)):
        snapshot = snaps[snap]['name']
        snap_info[snapshot] = {
            'size': snaps[snap]['size'],
            'source': snaps[snap]['source'],
            'created': snaps[snap]['created'],
            'tags': [],
        }
    if ACTIVE_DR_API in api_version:
        snaptags = array.list_volumes(snap=True, tags=True)
        for snaptag in range(0, len(snaptags)):
            snapname = snaptags[snaptag]['name']
            tagdict = {
                'key': snaptags[snaptag]['key'],
                'value': snaptags[snaptag]['value'],
                'namespace': snaptags[snaptag]['namespace']
            }
            snap_info[snapname]['tags'].append(tagdict)
    return snap_info


def generate_del_snap_dict(array):
    snap_info = {}
    api_version = array._list_available_rest_versions()
    snaps = array.list_volumes(snap=True, pending_only=True)
    for snap in range(0, len(snaps)):
        snapshot = snaps[snap]['name']
        snap_info[snapshot] = {
            'size': snaps[snap]['size'],
            'source': snaps[snap]['source'],
            'created': snaps[snap]['created'],
            'time_remaining': snaps[snap]['time_remaining'],
            'tags': [],
        }
    if ACTIVE_DR_API in api_version:
        snaptags = array.list_volumes(snap=True, tags=True, pending_only=True)
        for snaptag in range(0, len(snaptags)):
            snapname = snaptags[snaptag]['name']
            tagdict = {
                'key': snaptags[snaptag]['key'],
                'value': snaptags[snaptag]['value'],
                'namespace': snaptags[snaptag]['namespace']
            }
            snap_info[snapname]['tags'].append(tagdict)
    return snap_info


def generate_del_vol_dict(module, array):
    volume_info = {}
    api_version = array._list_available_rest_versions()
    vols = array.list_volumes(pending_only=True)
    for vol in range(0, len(vols)):
        volume = vols[vol]['name']
        volume_info[volume] = {
            'size': vols[vol]['size'],
            'source': vols[vol]['source'],
            'created': vols[vol]['created'],
            'serial': vols[vol]['serial'],
            'time_remaining': vols[vol]['time_remaining'],
            'tags': [],
        }
    if ACTIVE_DR_API in api_version:
        voltags = array.list_volumes(tags=True, pending_only=True)
        for voltag in range(0, len(voltags)):
            volume = voltags[voltag]['name']
            tagdict = {
                'key': voltags[voltag]['key'],
                'value': voltags[voltag]['value'],
                'copyable': voltags[voltag]['copyable'],
                'namespace': voltags[voltag]['namespace']
            }
            volume_info[volume]['tags'].append(tagdict)
    return volume_info


def generate_vol_dict(module, array):
    volume_info = {}
    vols = array.list_volumes()
    for vol in range(0, len(vols)):
        volume = vols[vol]['name']
        volume_info[volume] = {
            'protocol_endpoint': False,
            'source': vols[vol]['source'],
            'size': vols[vol]['size'],
            'serial': vols[vol]['serial'],
            'tags': [],
            'hosts': [],
            'bandwidth': ""
        }
    api_version = array._list_available_rest_versions()
    if AC_REQUIRED_API_VERSION in api_version:
        qvols = array.list_volumes(qos=True)
        for qvol in range(0, len(qvols)):
            volume = qvols[qvol]['name']
            qos = qvols[qvol]['bandwidth_limit']
            volume_info[volume]['bandwidth'] = qos
            if P53_API_VERSION in api_version:
                iops = qvols[qvol]['iops_limit']
                volume_info[volume]['iops_limit'] = iops
        vvols = array.list_volumes(protocol_endpoint=True)
        for vvol in range(0, len(vvols)):
            volume = vvols[vvol]['name']
            volume_info[volume] = {
                'protocol_endpoint': True,
                'source': vvols[vvol]['source'],
                'serial': vvols[vvol]['serial'],
                'tags': [],
                'hosts': [],
            }
        if P53_API_VERSION in array._list_available_rest_versions():
            pe_e2ees = array.list_volumes(protocol_endpoint=True, host_encryption_key=True)
            for pe_e2ee in range(0, len(pe_e2ees)):
                volume = pe_e2ees[pe_e2ee]['name']
                volume_info[volume]['host_encryption_key_status'] = pe_e2ees[pe_e2ee]['host_encryption_key_status']
        if P53_API_VERSION in array._list_available_rest_versions():
            e2ees = array.list_volumes(host_encryption_key=True)
            for e2ee in range(0, len(e2ees)):
                volume = e2ees[e2ee]['name']
                volume_info[volume]['host_encryption_key_status'] = e2ees[e2ee]['host_encryption_key_status']
    cvols = array.list_volumes(connect=True)
    for cvol in range(0, len(cvols)):
        volume = cvols[cvol]['name']
        voldict = {'host': cvols[cvol]['host'], 'lun': cvols[cvol]['lun']}
        volume_info[volume]['hosts'].append(voldict)
    if ACTIVE_DR_API in api_version:
        voltags = array.list_volumes(tags=True)
        for voltag in range(0, len(voltags)):
            volume = voltags[voltag]['name']
            tagdict = {
                'key': voltags[voltag]['key'],
                'value': voltags[voltag]['value'],
                'copyable': voltags[voltag]['copyable'],
                'namespace': voltags[voltag]['namespace']
            }
            volume_info[volume]['tags'].append(tagdict)
    return volume_info


def generate_host_dict(array):
    api_version = array._list_available_rest_versions()
    host_info = {}
    hosts = array.list_hosts()
    for host in range(0, len(hosts)):
        hostname = hosts[host]['name']
        tports = []
        host_all_info = array.get_host(hostname, all=True)
        if host_all_info:
            tports = host_all_info[0]['target_port']
        host_info[hostname] = {
            'hgroup': hosts[host]['hgroup'],
            'iqn': hosts[host]['iqn'],
            'wwn': hosts[host]['wwn'],
            'personality': array.get_host(hostname,
                                          personality=True)['personality'],
            'target_port': tports,
            'volumes': []
        }
        host_connections = array.list_host_connections(hostname)
        for connection in range(0, len(host_connections)):
            connection_dict = {
                'hostgroup': host_connections[connection]['hgroup'],
                'volume': host_connections[connection]['vol'],
                'lun': host_connections[connection]['lun']
            }
            host_info[hostname]['volumes'].append(connection_dict)
        if host_info[hostname]['iqn']:
            chap_data = array.get_host(hostname, chap=True)
            host_info[hostname]['target_user'] = chap_data['target_user']
            host_info[hostname]['host_user'] = chap_data['host_user']
        if NVME_API_VERSION in api_version:
            host_info[hostname]['nqn'] = hosts[host]['nqn']
    if PREFERRED_API_VERSION in api_version:
        hosts = array.list_hosts(preferred_array=True)
        for host in range(0, len(hosts)):
            hostname = hosts[host]['name']
            host_info[hostname]['preferred_array'] = hosts[host]['preferred_array']
    return host_info


def generate_pgroups_dict(array):
    pgroups_info = {}
    pgroups = array.list_pgroups()
    for pgroup in range(0, len(pgroups)):
        protgroup = pgroups[pgroup]['name']
        pgroups_info[protgroup] = {
            'hgroups': pgroups[pgroup]['hgroups'],
            'hosts': pgroups[pgroup]['hosts'],
            'source': pgroups[pgroup]['source'],
            'targets': pgroups[pgroup]['targets'],
            'volumes': pgroups[pgroup]['volumes'],
        }
        prot_sched = array.get_pgroup(protgroup, schedule=True)
        prot_reten = array.get_pgroup(protgroup, retention=True)
        if prot_sched['snap_enabled'] or prot_sched['replicate_enabled']:
            pgroups_info[protgroup]['snap_freqyency'] = prot_sched['snap_frequency']
            pgroups_info[protgroup]['replicate_freqyency'] = prot_sched['replicate_frequency']
            pgroups_info[protgroup]['snap_enabled'] = prot_sched['snap_enabled']
            pgroups_info[protgroup]['replicate_enabled'] = prot_sched['replicate_enabled']
            pgroups_info[protgroup]['snap_at'] = prot_sched['snap_at']
            pgroups_info[protgroup]['replicate_at'] = prot_sched['replicate_at']
            pgroups_info[protgroup]['replicate_blackout'] = prot_sched['replicate_blackout']
            pgroups_info[protgroup]['per_day'] = prot_reten['per_day']
            pgroups_info[protgroup]['target_per_day'] = prot_reten['target_per_day']
            pgroups_info[protgroup]['target_days'] = prot_reten['target_days']
            pgroups_info[protgroup]['days'] = prot_reten['days']
            pgroups_info[protgroup]['all_for'] = prot_reten['all_for']
            pgroups_info[protgroup]['target_all_for'] = prot_reten['target_all_for']
        if ":" in protgroup:
            snap_transfers = array.get_pgroup(protgroup, snap=True, transfer=True)
            pgroups_info[protgroup]['snaps'] = {}
            for snap_transfer in range(0, len(snap_transfers)):
                snap = snap_transfers[snap_transfer]['name']
                pgroups_info[protgroup]['snaps'][snap] = {
                    'created': snap_transfers[snap_transfer]['created'],
                    'started': snap_transfers[snap_transfer]['started'],
                    'completed': snap_transfers[snap_transfer]['completed'],
                    'physical_bytes_written': snap_transfers[snap_transfer]['physical_bytes_written'],
                    'data_transferred': snap_transfers[snap_transfer]['data_transferred'],
                    'progress': snap_transfers[snap_transfer]['progress'],
                }
    return pgroups_info


def generate_rl_dict(module, array):
    rl_info = {}
    api_version = array._list_available_rest_versions()
    if ACTIVE_DR_API in api_version:
        try:
            rlinks = array.list_pod_replica_links()
            for rlink in range(0, len(rlinks)):
                link_name = rlinks[rlink]['local_pod_name']
                since_epoch = rlinks[rlink]['recovery_point'] / 1000
                recovery_datatime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(since_epoch))
                rl_info[link_name] = {
                    'status': rlinks[rlink]['status'],
                    'direction': rlinks[rlink]['direction'],
                    'lag': str(rlinks[rlink]['lag'] / 1000) + 's',
                    'remote_pod_name': rlinks[rlink]['remote_pod_name'],
                    'remote_names': rlinks[rlink]['remote_names'],
                    'recovery_point': recovery_datatime,
                }
        except Exception:
            module.warn('Replica Links info requires purestorage SDK 1.19 or hisher')
    return rl_info


def generate_del_pods_dict(array):
    pods_info = {}
    api_version = array._list_available_rest_versions()
    if AC_REQUIRED_API_VERSION in api_version:
        pods = array.list_pods(mediator=True, pending_only=True)
        for pod in range(0, len(pods)):
            acpod = pods[pod]['name']
            pods_info[acpod] = {
                'source': pods[pod]['source'],
                'arrays': pods[pod]['arrays'],
                'mediator': pods[pod]['mediator'],
                'mediator_version': pods[pod]['mediator_version'],
                'time_remaining': pods[pod]['time_remaining'],
            }
            if ACTIVE_DR_API in api_version:
                if pods_info[acpod]['arrays'][0]['frozen_at']:
                    frozen_time = pods_info[acpod]['arrays'][0]['frozen_at'] / 1000
                    frozen_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(frozen_time))
                    pods_info[acpod]['arrays'][0]['frozen_at'] = frozen_datetime
                pods_info[acpod]['link_source_count'] = pods[pod]['link_source_count']
                pods_info[acpod]['link_target_count'] = pods[pod]['link_target_count']
                pods_info[acpod]['promotion_status'] = pods[pod]['promotion_status']
                pods_info[acpod]['requested_promotion_state'] = pods[pod]['requested_promotion_state']
        if PREFERRED_API_VERSION in api_version:
            pods_fp = array.list_pods(failover_preference=True, pending_only=True)
            for pod in range(0, len(pods_fp)):
                acpod = pods_fp[pod]['name']
                pods_info[acpod]['failover_preference'] = pods_fp[pod]['failover_preference']
    return pods_info


def generate_pods_dict(array):
    pods_info = {}
    api_version = array._list_available_rest_versions()
    if AC_REQUIRED_API_VERSION in api_version:
        pods = array.list_pods(mediator=True)
        for pod in range(0, len(pods)):
            acpod = pods[pod]['name']
            pods_info[acpod] = {
                'source': pods[pod]['source'],
                'arrays': pods[pod]['arrays'],
                'mediator': pods[pod]['mediator'],
                'mediator_version': pods[pod]['mediator_version'],
            }
            if ACTIVE_DR_API in api_version:
                if pods_info[acpod]['arrays'][0]['frozen_at']:
                    frozen_time = pods_info[acpod]['arrays'][0]['frozen_at'] / 1000
                    frozen_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(frozen_time))
                    pods_info[acpod]['arrays'][0]['frozen_at'] = frozen_datetime
                pods_info[acpod]['link_source_count'] = pods[pod]['link_source_count']
                pods_info[acpod]['link_target_count'] = pods[pod]['link_target_count']
                pods_info[acpod]['promotion_status'] = pods[pod]['promotion_status']
                pods_info[acpod]['requested_promotion_state'] = pods[pod]['requested_promotion_state']
        if PREFERRED_API_VERSION in api_version:
            pods_fp = array.list_pods(failover_preference=True)
            for pod in range(0, len(pods_fp)):
                acpod = pods_fp[pod]['name']
                pods_info[acpod]['failover_preference'] = pods_fp[pod]['failover_preference']
    return pods_info


def generate_conn_array_dict(array):
    conn_array_info = {}
    api_version = array._list_available_rest_versions()
    carrays = array.list_array_connections()
    for carray in range(0, len(carrays)):
        arrayname = carrays[carray]['array_name']
        conn_array_info[arrayname] = {
            'array_id': carrays[carray]['id'],
            'throttled': carrays[carray]['throttled'],
            'version': carrays[carray]['version'],
            'type': carrays[carray]['type'],
            'mgmt_ip': carrays[carray]['management_address'],
            'repl_ip': carrays[carray]['replication_address'],
        }
        if P53_API_VERSION in api_version:
            conn_array_info[arrayname]['status'] = carrays[carray]['status']
        else:
            conn_array_info[arrayname]['connected'] = carrays[carray]['connected']
    throttles = array.list_array_connections(throttle=True)
    for throttle in range(0, len(throttles)):
        arrayname = throttles[throttle]['array_name']
        if conn_array_info[arrayname]['throttled']:
            conn_array_info[arrayname]['throttling'] = {
                'default_limit': throttles[throttle]['default_limit'],
                'window_limit': throttles[throttle]['window_limit'],
                'window': throttles[throttle]['window'],
            }
    return conn_array_info


def generate_apps_dict(array):
    apps_info = {}
    api_version = array._list_available_rest_versions()
    if SAN_REQUIRED_API_VERSION in api_version:
        apps = array.list_apps()
        for app in range(0, len(apps)):
            appname = apps[app]['name']
            apps_info[appname] = {
                'version': apps[app]['version'],
                'status': apps[app]['status'],
                'description': apps[app]['description'],
            }
    if P53_API_VERSION in api_version:
        app_nodes = array.list_app_nodes()
        for app in range(0, len(app_nodes)):
            appname = app_nodes[app]['name']
            apps_info[appname]['index'] = app_nodes[app]['index']
            apps_info[appname]['vnc'] = app_nodes[app]['vnc']
    return apps_info


def generate_vgroups_dict(array):
    vgroups_info = {}
    api_version = array._list_available_rest_versions()
    if AC_REQUIRED_API_VERSION in api_version:
        vgroups = array.list_vgroups()
        for vgroup in range(0, len(vgroups)):
            virtgroup = vgroups[vgroup]['name']
            vgroups_info[virtgroup] = {
                'volumes': vgroups[vgroup]['volumes'],
            }
    return vgroups_info


def generate_certs_dict(array):
    certs_info = {}
    api_version = array._list_available_rest_versions()
    if P53_API_VERSION in api_version:
        certs = array.list_certificates()
        for cert in range(0, len(certs)):
            certificate = certs[cert]['name']
            valid_from = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(certs[cert]['valid_from'] / 1000))
            valid_to = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(certs[cert]['valid_to'] / 1000))
            certs_info[certificate] = {
                'status': certs[cert]['status'],
                'issued_to': certs[cert]['issued_to'],
                'valid_from': valid_from,
                'locality': certs[cert]['locality'],
                'country': certs[cert]['country'],
                'issued_by': certs[cert]['issued_by'],
                'valid_to': valid_to,
                'state': certs[cert]['state'],
                'key_size': certs[cert]['key_size'],
                'org_unit': certs[cert]['organizational_unit'],
                'common_name': certs[cert]['common_name'],
                'organization': certs[cert]['organization'],
                'email': certs[cert]['email'],
            }
    return certs_info


def generate_kmip_dict(array):
    kmip_info = {}
    api_version = array._list_available_rest_versions()
    if P53_API_VERSION in api_version:
        kmips = array.list_kmip()
        for kmip in range(0, len(kmips)):
            key = kmips[kmip]['name']
            kmip_info[key] = {
                'certificate': kmips[kmip]['certificate'],
                'ca_cert_configured': kmips[kmip]['ca_certificate_configured'],
                'uri': kmips[kmip]['uri'],
            }
    return kmip_info


def generate_nfs_offload_dict(array):
    offload_info = {}
    api_version = array._list_available_rest_versions()
    if AC_REQUIRED_API_VERSION in api_version:
        offload = array.list_nfs_offload()
        for target in range(0, len(offload)):
            offloadt = offload[target]['name']
            offload_info[offloadt] = {
                'status': offload[target]['status'],
                'mount_point': offload[target]['mount_point'],
                'protocol': offload[target]['protocol'],
                'mount_options': offload[target]['mount_options'],
                'address': offload[target]['address'],
            }
    return offload_info


def generate_s3_offload_dict(array):
    offload_info = {}
    api_version = array._list_available_rest_versions()
    if S3_REQUIRED_API_VERSION in api_version:
        offload = array.list_s3_offload()
        for target in range(0, len(offload)):
            offloadt = offload[target]['name']
            offload_info[offloadt] = {
                'status': offload[target]['status'],
                'bucket': offload[target]['bucket'],
                'protocol': offload[target]['protocol'],
                'access_key_id': offload[target]['access_key_id'],
            }
            if P53_API_VERSION in api_version:
                offload_info[offloadt]['placement_strategy'] = offload[target]['placement_strategy']
    return offload_info


def generate_azure_offload_dict(array):
    offload_info = {}
    api_version = array._list_available_rest_versions()
    if P53_API_VERSION in api_version:
        offload = array.list_azure_offload()
        for target in range(0, len(offload)):
            offloadt = offload[target]['name']
            offload_info[offloadt] = {
                'status': offload[target]['status'],
                'account_name': offload[target]['account_name'],
                'protocol': offload[target]['protocol'],
                'secret_access_key': offload[target]['secret_access_key'],
                'container_name': offload[target]['container_name'],
            }
    return offload_info


def generate_hgroups_dict(array):
    hgroups_info = {}
    hgroups = array.list_hgroups()
    for hgroup in range(0, len(hgroups)):
        hostgroup = hgroups[hgroup]['name']
        hgroups_info[hostgroup] = {
            'hosts': hgroups[hgroup]['hosts'],
            'pgs': [],
            'vols': [],
        }
    pghgroups = array.list_hgroups(protect=True)
    for pghg in range(0, len(pghgroups)):
        pgname = pghgroups[pghg]['name']
        hgroups_info[pgname]['pgs'].append(pghgroups[pghg]['protection_group'])
    volhgroups = array.list_hgroups(connect=True)
    for pgvol in range(0, len(volhgroups)):
        pgname = volhgroups[pgvol]['name']
        volpgdict = [volhgroups[pgvol]['vol'], volhgroups[pgvol]['lun']]
        hgroups_info[pgname]['vols'].append(volpgdict)
    return hgroups_info


def generate_interfaces_dict(array):
    api_version = array._list_available_rest_versions()
    int_info = {}
    ports = array.list_ports()
    for port in range(0, len(ports)):
        int_name = ports[port]['name']
        if ports[port]['wwn']:
            int_info[int_name] = ports[port]['wwn']
        if ports[port]['iqn']:
            int_info[int_name] = ports[port]['iqn']
        if NVME_API_VERSION in api_version:
            if ports[port]['nqn']:
                int_info[int_name] = ports[port]['nqn']
    return int_info


def main():
    argument_spec = purefa_argument_spec()
    argument_spec.update(dict(
        gather_subset=dict(default='minimum', type='list',)
    ))

    module = AnsibleModule(argument_spec, supports_check_mode=False)
    array = get_system(module)

    subset = [test.lower() for test in module.params['gather_subset']]
    valid_subsets = ('all', 'minimum', 'config', 'performance', 'capacity',
                     'network', 'subnet', 'interfaces', 'hgroups', 'pgroups',
                     'hosts', 'admins', 'volumes', 'snapshots', 'pods', 'replication',
                     'vgroups', 'offload', 'apps', 'arrays', 'certs', 'kmip')
    subset_test = (test in valid_subsets for test in subset)
    if not all(subset_test):
        module.fail_json(msg="value must gather_subset must be one or more of: %s, got: %s"
                         % (",".join(valid_subsets), ",".join(subset)))

    info = {}

    if 'minimum' in subset or 'all' in subset or 'apps' in subset:
        info['default'] = generate_default_dict(array)
    if 'performance' in subset or 'all' in subset:
        info['performance'] = generate_perf_dict(array)
    if 'config' in subset or 'all' in subset:
        info['config'] = generate_config_dict(module, array)
    if 'capacity' in subset or 'all' in subset:
        info['capacity'] = generate_capacity_dict(array)
    if 'network' in subset or 'all' in subset:
        info['network'] = generate_network_dict(array)
    if 'subnet' in subset or 'all' in subset:
        info['subnet'] = generate_subnet_dict(array)
    if 'interfaces' in subset or 'all' in subset:
        info['interfaces'] = generate_interfaces_dict(array)
    if 'hosts' in subset or 'all' in subset:
        info['hosts'] = generate_host_dict(array)
    if 'volumes' in subset or 'all' in subset:
        info['volumes'] = generate_vol_dict(module, array)
        info['deleted_volumes'] = generate_del_vol_dict(module, array)
    if 'snapshots' in subset or 'all' in subset:
        info['snapshots'] = generate_snap_dict(array)
        info['deleted_snapshots'] = generate_del_snap_dict(array)
    if 'hgroups' in subset or 'all' in subset:
        info['hgroups'] = generate_hgroups_dict(array)
    if 'pgroups' in subset or 'all' in subset:
        info['pgroups'] = generate_pgroups_dict(array)
    if 'pods' in subset or 'all' in subset or 'replication' in subset:
        info['replica_links'] = generate_rl_dict(module, array)
        info['pods'] = generate_pods_dict(array)
        info['deleted_pods'] = generate_del_pods_dict(array)
    if 'admins' in subset or 'all' in subset:
        info['admins'] = generate_admin_dict(array)
    if 'vgroups' in subset or 'all' in subset:
        info['vgroups'] = generate_vgroups_dict(array)
    if 'offload' in subset or 'all' in subset:
        info['azure_offload'] = generate_azure_offload_dict(array)
        info['nfs_offload'] = generate_nfs_offload_dict(array)
        info['s3_offload'] = generate_s3_offload_dict(array)
    if 'apps' in subset or 'all' in subset:
        if 'CBS' not in info['default']['array_model']:
            info['apps'] = generate_apps_dict(array)
        else:
            info['apps'] = {}
    if 'arrays' in subset or 'all' in subset:
        info['arrays'] = generate_conn_array_dict(array)
    if 'certs' in subset or 'all' in subset:
        info['certs'] = generate_certs_dict(array)
    if 'kmip' in subset or 'all' in subset:
        info['kmip'] = generate_kmip_dict(array)

    module.exit_json(changed=False, purefa_info=info)


if __name__ == '__main__':
    main()
