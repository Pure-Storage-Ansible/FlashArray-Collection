
purefa_snap -- Manage volume snapshots on Pure Storage FlashArrays
==================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Create or delete volumes and volume snapshots on Pure Storage FlashArray.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  state (optional, str, present)
    Define whether the volume snapshot should exist or not.


  suffix (optional, str, None)
    Suffix of snapshot name.


  target (optional, str, None)
    Name of target volume if creating from snapshot.


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  eradicate (optional, bool, no)
    Define whether to eradicate the snapshot on delete or leave in trash.


  fa_url (True, str, None)
    FlashArray management IPv4 address or Hostname.


  overwrite (optional, bool, no)
    Define whether to overwrite existing volume when creating from snapshot.


  name (True, str, None)
    The name of the source volume.





Notes
-----

.. note::
   - This module requires the ``purestorage`` Python library
   - You must set ``PUREFA_URL`` and ``PUREFA_API`` environment variables if *fa_url* and *api_token* arguments are not passed to the module directly




Examples
--------

.. code-block:: yaml+jinja

    
    - name: Create snapshot foo.ansible
      purefa_snap:
        name: foo
        suffix: ansible
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: present
    
    - name: Create R/W clone foo_clone from snapshot foo.snap
      purefa_snap:
        name: foo
        suffix: snap
        target: foo_clone
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: copy
    
    - name: Overwrite existing volume foo_clone with snapshot foo.snap
      purefa_snap:
        name: foo
        suffix: snap
        target: foo_clone
        overwrite: true
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: copy
    
    - name: Delete and eradicate snapshot named foo.snap
      purefa_snap:
        name: foo
        suffix: snap
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

