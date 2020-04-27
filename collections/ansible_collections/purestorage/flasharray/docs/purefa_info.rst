
purefa_info -- Collect information from Pure Storage FlashArray
===============================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Collect information from a Pure Storage Flasharray running the Purity//FA operating system. By default, the module will collect basic information including hosts, host groups, protection groups and volume counts. Additional information can be collected based on the configured set of arguements.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  gather_subset (False, list, minimum)
    When supplied, this argument will define the information to be collected. Possible values for this include all, minimum, config, performance, capacity, network, subnet, interfaces, hgroups, pgroups, hosts, admins, volumes, snapshots, pods, vgroups, offload, apps, arrays, certs and kmip.


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  fa_url (True, str, None)
    FlashArray management IPv4 address or Hostname.





Notes
-----

.. note::
   - This module requires the ``purestorage`` Python library
   - You must set ``PUREFA_URL`` and ``PUREFA_API`` environment variables if *fa_url* and *api_token* arguments are not passed to the module directly




Examples
--------

.. code-block:: yaml+jinja

    
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


Return Values
-------------

  purefa_info (always, complex, {'subnet': {}, 'interfaces': {'CT1.ETH4': 'iqn.2010-06.com.purestorage:flasharray.2111b767484e4682', 'CT0.ETH4': 'iqn.2010-06.com.purestorage:flasharray.2111b767484e4682'}, 'snapshots': {'@offload_boot.1': {'source': '@offload_boot', 'created': '2019-03-14T15:29:20Z', 'size': 68719476736}}, 'nfs_offload': {}, 'vgroups': {'test': {'volumes': ['test/test', 'test/test1']}}, 'capacity': {'system_space': 0, 'snapshot_space': 284597118, 'total_capacity': 7002920315199, 'free_space': 6995782867042, 'provisioned_space': 442391871488, 'data_reduction': 11.664774599686346, 'shared_space': 3070918120, 'volume_space': 3781932919, 'thin_provisioning': 0.8201773449669771, 'total_reduction': 64.86821472825108}, 'network': {'@offload.data0': {'hwaddr': '52:54:30:02:b9:4e', 'netmask': '255.255.255.0', 'address': '10.21.200.222', 'services': ['app'], 'speed': 10000000000, 'gateway': '10.21.200.1', 'mtu': 1500}, 'ct0.eth0': {'hwaddr': 'ec:f4:bb:c8:8a:04', 'netmask': '255.255.255.0', 'address': '10.21.200.211', 'services': ['management'], 'speed': 1000000000, 'gateway': '10.21.200.1', 'mtu': 1500}, 'ct0.eth2': {'hwaddr': 'ec:f4:bb:c8:8a:00', 'netmask': '255.255.255.0', 'address': '10.21.200.218', 'services': ['replication'], 'speed': 10000000000, 'gateway': None, 'mtu': 1500}, 'ct1.eth4': {'hwaddr': '90:e2:ba:8b:b1:8c', 'netmask': '255.255.255.0', 'address': '10.21.200.216', 'services': ['iscsi'], 'speed': 10000000000, 'gateway': None, 'mtu': 1500}, 'ct0.eth4': {'hwaddr': '90:e2:ba:83:79:0c', 'netmask': '255.255.255.0', 'address': '10.21.200.214', 'services': ['iscsi'], 'speed': 10000000000, 'gateway': None, 'mtu': 1500}, 'ct1.eth2': {'hwaddr': 'ec:f4:bb:e4:c6:38', 'netmask': '255.255.255.0', 'address': '10.21.200.220', 'services': ['replication'], 'speed': 10000000000, 'gateway': None, 'mtu': 1500}, 'ct1.eth0': {'hwaddr': 'ec:f4:bb:e4:c6:3c', 'netmask': '255.255.255.0', 'address': '10.21.200.212', 'services': ['management'], 'speed': 1000000000, 'gateway': '10.21.200.1', 'mtu': 1500}, 'vir0': {'hwaddr': 'fe:ba:e9:e7:6b:0f', 'netmask': '255.255.255.0', 'address': '10.21.200.210', 'services': ['management'], 'speed': 1000000000, 'gateway': '10.21.200.1', 'mtu': 1500}}, 'arrays': {}, 'config': {'ntp': ['prod-ntp1.puretec.purestorage.com'], 'scsi_timeout': 60, 'snmp': [{'name': 'manager1', 'notification': 'trap', 'community': '', 'privacy_protocol': None, 'auth_protocol': None, 'host': '10.21.23.34', 'version': 'v2c', 'user': None, 'privacy_passphrase': None, 'auth_passphrase': None}], 'phonehome': 'enabled', 'syslog': ['udp://prod-ntp2.puretec.purestorage.com:333'], 'idle_timeout': 0, 'proxy': '', 'dns': {'nameservers': ['8.8.4.4'], 'domain': 'acme.com'}, 'global_admin': {'min_password_length': 1, 'lockout_duration': None, 'single_sign_on_enabled': False, 'max_login_attempts': None}, 'relayhost': 'smtp.puretec.purestorage.com', 'smtp': [{'enabled': True, 'name': 'flasharray-alerts@purestorage.com'}], 'senderdomain': 'purestorage.com', 'directory_service': {'bind_user': None, 'enabled': False, 'uri': [], 'user_login_attribute': None, 'user_object_class': None, 'bind_password': None, 'base_dn': None, 'check_peer': False}, 'directory_service_roles': {'ops_admin': {'group_base': None, 'group': None}, 'readonly': {'group_base': None, 'group': None}, 'array_admin': {'group_base': None, 'group': None}, 'storage_admin': {'group_base': None, 'group': None}}}, 'pgroups': {'test_pg': {'source': 'docker-host', 'hosts': None, 'targets': None, 'volumes': None, 'hgroups': None}}, 'apps': {'offload': {'status': 'healthy', 'version': '5.2.1', 'description': 'Snapshot offload to NFS or Amazon S3'}}, 's3_offload': {'s3-offload': {'status': 'connected', 'bucket': 'offload-bucket', 'protocol': 's3', 'access_key_id': 'AKIAILNVEPWZTV4FGWZQ'}}, 'hgroups': {}, 'default': {'array_model': 'FA-405', 'hostgroups': 0, 'protection_groups': 1, 'snapshots': 2, 'volume_groups': 1, 'admins': 1, 'hosts': 15, 'connected_arrays': 0, 'purity_version': '5.2.1', 'connection_key': 'c6033033-fe69-2515-a9e8-966bb7fe4b40', 'pods': 1, 'array_name': 'array'}, 'admins': {'pureuser': {'role': 'array_admin', 'type': 'local'}}, 'hosts': {'@offload': {'preferred_array': [], 'iqn': [], 'target_port': [], 'personality': None, 'wwn': [], 'nqn': [], 'hgroup': None}, 'docker-host': {'preferred_array': [], 'iqn': ['iqn.1994-05.com.redhat:d97adf78472'], 'target_port': ['CT0.ETH4', 'CT1.ETH4'], 'personality': None, 'wwn': [], 'nqn': [], 'hgroup': None}}, 'volumes': {'docker-store': {'source': None, 'bandwidth': None, 'hosts': [['docker-host', 1]], 'serial': '43BE47C12334399B00011418', 'size': 21474836480}, '@offload_boot': {'source': None, 'bandwidth': None, 'hosts': [['@offload', 1]], 'serial': '43BE47C12334399B00013959', 'size': 68719476736}}, 'performance': {'writes_per_sec': 0, 'local_queue_usec_per_op': 0, 'qos_rate_limit_usec_per_read_op': 0, 'queue_usec_per_write_op': 0, 'output_per_sec': 0, 'san_usec_per_read_op': 0, 'qos_rate_limit_usec_per_write_op': 0, 'reads_per_sec': 0, 'queue_usec_per_read_op': 0, 'input_per_sec': 0, 'time': '2019-08-14T21:33:51Z', 'san_usec_per_write_op': 0, 'usec_per_read_op': 0, 'queue_depth': 0, 'usec_per_write_op': 0}, 'pods': {'test': {'arrays': [{'status': 'online', 'array_id': '043be47c-1233-4399-b9d6-8fe38727dd9d', 'name': 'array2', 'mediator_status': 'online'}], 'source': None}}})
    Returns the information collected from the FlashArray




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

