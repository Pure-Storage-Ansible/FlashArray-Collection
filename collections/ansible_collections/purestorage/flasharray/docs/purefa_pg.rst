
purefa_pg -- Manage protection groups on Pure Storage FlashArrays
=================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Create, delete or modify protection groups on Pure Storage FlashArrays.

If a protection group exists and you try to add non-valid types, eg. a host to a volume protection group the module will ignore the invalid types.

Protection Groups on Offload targets are supported.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  target (optional, list, None)
    List of remote arrays or offload target for replication protection group to connect to.

    Note that all replicated protection groups are asynchronous.

    Target arrays or offload targets must already be connected to the source array.

    Maximum number of targets per Portection Group is 4, assuming your configuration suppors this.


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  enabled (optional, bool, yes)
    Define whether to enabled snapshots for the protection group.


  state (optional, str, present)
    Define whether the protection group should exist or not.


  hostgroup (optional, list, None)
    List of existing hostgroups to add to protection group.


  volume (optional, list, None)
    List of existing volumes to add to protection group.


  host (optional, list, None)
    List of existing hosts to add to protection group.


  pgroup (True, str, None)
    The name of the protection group.


  fa_url (True, str, None)
    FlashArray management IPv4 address or Hostname.


  eradicate (optional, bool, no)
    Define whether to eradicate the protection group on delete and leave in trash.





Notes
-----

.. note::
   - This module requires the ``purestorage`` Python library
   - You must set ``PUREFA_URL`` and ``PUREFA_API`` environment variables if *fa_url* and *api_token* arguments are not passed to the module directly




Examples
--------

.. code-block:: yaml+jinja

    
    - name: Create new local protection group
      purefa_pg:
        pgroup: foo
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Create new replicated protection group
      purefa_pg:
        pgroup: foo
        target:
          - arrayb
          - arrayc
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Create new replicated protection group to offload target and remote array
      purefa_pg:
        pgroup: foo
        target:
          - offload
          - arrayc
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Create new protection group with snapshots disabled
      purefa_pg:
        pgroup: foo
        enabled: false
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Delete protection group
      purefa_pg:
        pgroup: foo
        eradicate: true
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: absent
    
    - name: Eradicate protection group foo on offload target where source array is arrayA
      purefa_pg:
        pgroup: "arrayA:foo"
        target: offload
        eradicate: true
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: absent
    
    - name: Create protection group for hostgroups
      purefa_pg:
        pgroup: bar
        hostgroup:
          - hg1
          - hg2
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Create protection group for hosts
      purefa_pg:
        pgroup: bar
        host:
          - host1
          - host2
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Create replicated protection group for volumes
      purefa_pg:
        pgroup: bar
        volume:
          - vol1
          - vol2
        target: arrayb
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

