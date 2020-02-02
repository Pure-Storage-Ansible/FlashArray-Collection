
purefa_hg -- Manage hostgroups on Pure Storage FlashArrays
==========================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Create, delete or modifiy hostgroups on Pure Storage FlashArrays.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  host (optional, list, None)
    List of existing hosts to add to hostgroup.


  hostgroup (True, str, None)
    The name of the hostgroup.


  volume (optional, list, None)
    List of existing volumes to add to hostgroup.


  state (optional, str, present)
    Define whether the hostgroup should exist or not.


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  lun (optional, int, None)
    LUN ID to assign to volume for hostgroup. Must be unique.

    Only applicable when only one volume is specified for connection.

    If not provided the ID will be automatically assigned.

    Range for LUN ID is 1 to 4095.


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

    
    - name: Create empty hostgroup
      purefa_hg:
        hostgroup: foo
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Add hosts and volumes to existing or new hostgroup
      purefa_hg:
        hostgroup: foo
        host:
          - host1
          - host2
        volume:
          - vol1
          - vol2
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Delete hosts and volumes from hostgroup
      purefa_hg:
        hostgroup: foo
        host:
          - host1
          - host2
        volume:
          - vol1
          - vol2
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: absent
    
    # This will disconnect all hosts and volumes in the hostgroup
    - name: Delete hostgroup
      purefa_hg:
        hostgroup: foo
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: absent
    
    - name: Create host group with hosts and volumes
      purefa_hg:
        hostgroup: bar
        host:
          - host1
          - host2
        volume:
          - vol1
          - vol2
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

