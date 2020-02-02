
purefa_host -- Manage hosts on Pure Storage FlashArrays
=======================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Create, delete or modify hosts on Pure Storage FlashArrays.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  fa_url (True, str, None)
    FlashArray management IPv4 address or Hostname.


  preferred_array (optional, list, None)
    List of preferred arrays in an ActiveCluster environment.

    To remove existing preferred arrays from the host, specify *delete*.


  protocol (optional, str, iscsi)
    Defines the host connection protocol for volumes.


  name (True, str, None)
    The name of the host.


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  target_user (optional, str, None)
    Sets the target user name for CHAP authentication

    Required with *target_password*

    To clear the username/password pair use *clear* as the password


  volume (optional, str, None)
    Volume name to map to the host.


  state (optional, str, present)
    Define whether the host should exist or not.

    When removing host all connected volumes will be disconnected.


  iqn (optional, list, None)
    List of IQNs of the host if protocol is iscsi or mixed.


  host_user (optional, str, None)
    Sets the host user name for CHAP authentication

    Required with *host_password*

    To clear the username/password pair use *clear* as the password


  host_password (optional, str, None)
    Sets the host password for CHAP authentication

    Password length between 12 and 255 characters

    To clear the username/password pair use *clear* as the password

    SETTING A PASSWORD IS NON-IDEMPOTENT


  target_password (optional, str, None)
    Sets the target password for CHAP authentication

    Password length between 12 and 255 characters

    To clear the username/password pair use *clear* as the password

    SETTING A PASSWORD IS NON-IDEMPOTENT


  wwns (optional, list, None)
    List of wwns of the host if protocol is fc or mixed.


  nqn (optional, list, None)
    List of NQNs of the host if protocol is nvme or mixed.


  lun (optional, int, None)
    LUN ID to assign to volume for host. Must be unique.

    If not provided the ID will be automatically assigned.

    Range for LUN ID is 1 to 4095.


  personality (optional, str, )
    Define which operating system the host is. Recommended for ActiveCluster integration.





Notes
-----

.. note::
   - If specifying ``lun`` option ensure host support requested value
   - This module requires the ``purestorage`` Python library
   - You must set ``PUREFA_URL`` and ``PUREFA_API`` environment variables if *fa_url* and *api_token* arguments are not passed to the module directly




Examples
--------

.. code-block:: yaml+jinja

    
    - name: Create new AIX host
      purefa_host:
        host: foo
        personality: aix
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Delete host
      purefa_host:
        host: foo
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: absent
    
    - name: Make host bar with wwn ports
      purefa_host:
        host: bar
        protocol: fc
        wwns:
        - 00:00:00:00:00:00:00
        - 11:11:11:11:11:11:11
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Make host bar with iSCSI ports
      purefa_host:
        host: bar
        protocol: iscsi
        iqn:
        - iqn.1994-05.com.redhat:7d366003913
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Make host bar with NVMe ports
      purefa_host:
        host: bar
        protocol: nvme
        nqn:
        - nqn.2014-08.com.vendor:nvme:nvm-subsystem-sn-d78432
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Make mixed protocol host
      purefa_host:
        host: bar
        protocol: mixed
        nqn:
        - nqn.2014-08.com.vendor:nvme:nvm-subsystem-sn-d78432
        iqn:
        - iqn.1994-05.com.redhat:7d366003914
        wwns:
        - 00:00:00:00:00:00:01
        - 11:11:11:11:11:11:12
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Map host foo to volume bar as LUN ID 12
      purefa_host:
        host: foo
        volume: bar
        lun: 12
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Disconnect volume bar from host foo
      purefa_host:
        host: foo
        volume: bar
        state: absent
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Add preferred arrays to host foo
      purefa_host:
        host: foo
        preferred_array:
        - array1
        - array2
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Delete preferred arrays from host foo
      purefa_host:
        host: foo
        preferred_array: delete
        fa_url: 10.10.10.2
    
    - name: Set CHAP target and host username/password pairs
      purefa_host:
        host: foo
        target_user: user1
        target_password: passwrodpassword
        host_user: user2
        host_password: passwrodpassword
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Delete CHAP target and host username/password pairs
      purefa_host:
        host: foo
        target_user: user
        target_password: clear
        host_user: user
        host_password: clear
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

