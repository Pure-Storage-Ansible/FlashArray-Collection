
purefa_vg -- Manage volume groups on Pure Storage FlashArrays
=============================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Create, delete or modify volume groups on Pure Storage FlashArrays.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  name (True, str, None)
    The name of the volume group.


  iops_qos (optional, str, None)
    IOPs limit for vgroup - use value or K or M K will mean 1000 M will mean 1000000 To clear an existing IOPs setting use 0 (zero)


  state (optional, str, present)
    Define whether the volume group should exist or not.


  bw_qos (optional, str, None)
    Bandwidth limit for vgroup in M or G units. M will set MB/s G will set GB/s To clear an existing QoS setting use 0 (zero)


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  fa_url (True, str, None)
    FlashArray management IPv4 address or Hostname.


  eradicate (optional, bool, no)
    Define whether to eradicate the volume group on delete and leave in trash.





Notes
-----

.. note::
   - This module requires the ``purestorage`` Python library
   - You must set ``PUREFA_URL`` and ``PUREFA_API`` environment variables if *fa_url* and *api_token* arguments are not passed to the module directly




Examples
--------

.. code-block:: yaml+jinja

    
    - name: Create new volune group
      purefa_vg:
        name: foo
        bw_qos: 50M
        iops_qos: 100
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    - name: Update volune group QoS limits
      purefa_vg:
        name: foo
        bw_qos: 0
        iops_qos: 5555
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    - name: Destroy volume group
      purefa_vg:
        name: foo
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: absent
    - name: Recover deleted volune group
      purefa_vg:
        name: foo
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    - name: Destroy and Eradicate volume group
      purefa_vg:
        name: foo
        eradicate: true
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: absent




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

