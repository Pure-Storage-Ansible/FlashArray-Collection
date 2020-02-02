
purefa_volume -- Manage volumes on Pure Storage FlashArrays
===========================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Create, delete or extend the capacity of a volume on Pure Storage FlashArray.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  rename (optional, str, None)
    Value to rename the specified volume to.

    Rename only applies to the container the current volumes is in.

    There is no requirement to specify the pod or vgroup name as this is implied.


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  name (True, str, None)
    The name of the volume.


  move (optional, str, None)
    Move a volume in and out of a pod or vgroup

    Provide the name of pod or vgroup to move the volume to

    Pod and Vgroup names must be unique in the array

    To move to the local array, specify ``local``

    This is not idempotent - use ``ignore_errors`` in the play


  fa_url (True, str, None)
    FlashArray management IPv4 address or Hostname.


  iops_qos (optional, str, None)
    IOPs limit for volume - use value or K or M K will mean 1000 M will mean 1000000 To clear an existing IOPs setting use 0 (zero)


  state (optional, str, present)
    Define whether the volume should exist or not.


  size (optional, str, None)
    Volume size in M, G, T or P units.


  target (optional, str, None)
    The name of the target volume, if copying.


  eradicate (optional, bool, no)
    Define whether to eradicate the volume on delete or leave in trash.


  overwrite (optional, bool, no)
    Define whether to overwrite a target volume if it already exisits.


  bw_qos (optional, str, None)
    Bandwidth limit for volume in M or G units. M will set MB/s G will set GB/s To clear an existing QoS setting use 0 (zero)





Notes
-----

.. note::
   - This module requires the ``purestorage`` Python library
   - You must set ``PUREFA_URL`` and ``PUREFA_API`` environment variables if *fa_url* and *api_token* arguments are not passed to the module directly




Examples
--------

.. code-block:: yaml+jinja

    
    - name: Create new volume named foo with a QoS limit
      purefa_volume:
        name: foo
        size: 1T
        bw_qos: 58M
        iops_qos: 23K
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: present
    
    - name: Extend the size of an existing volume named foo
      purefa_volume:
        name: foo
        size: 2T
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: present
    
    - name: Delete and eradicate volume named foo
      purefa_volume:
        name: foo
        eradicate: yes
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: absent
    
    - name: Create clone of volume bar named foo
      purefa_volume:
        name: foo
        target: bar
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: present
    
    - name: Overwrite volume bar with volume foo
      purefa_volume:
        name: foo
        target: bar
        overwrite: yes
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: present
    
    - name: Clear volume QoS from volume foo
      purefa_volume:
        name: foo
        bw_qos: 0
        iops_qos: 0
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: present
    
    - name: Move local volume foo from local array to pod bar
      purefa_volume:
        name: foo
        move: bar
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Move volume foo in pod bar to local array
      purefa_volume:
        name: bar::foo
        move: local
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Move volume foo in pod bar to vgroup fin
      purefa_volume:
        name: bar::foo
        move: fin
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592


Return Values
-------------

  volume (success, dict, )
    A dictionary describing the changed volume.  Only some attributes below will be returned with various actions.

    source (, str, )
      Volume name of source volume used for volume copy

    iops_limit (, int, )
      Volume IOPs limit

    created (, str, 2019-03-13T22:49:24Z)
      Volume creation time

    serial (, str, 361019ECACE43D83000120A4)
      Volume serial number

    size (, int, )
      Volume size in bytes

    bandwidth_limit (, int, )
      Volume bandwidth limit in bytes/sec

    name (, str, )
      Volume name





Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

