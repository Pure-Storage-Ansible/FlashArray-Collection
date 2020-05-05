
purefa_pgsnap -- Manage protection group snapshots on Pure Storage FlashArrays
==============================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Create or delete protection group snapshots on Pure Storage FlashArray.

Recovery of replicated snapshots on the replica target array is enabled.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  apply_retention (optional, bool, False)
    Apply retention schedule settings to the snapshot


  restore (optional, str, None)
    Restore a specific volume from a protection group snapshot.


  offload (optional, str, None)
    Name of offload target on which the snapshot exists.

    This is only applicable for deletion and erasure of snapshots


  name (True, str, None)
    The name of the source protection group.


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  fa_url (True, str, None)
    FlashArray management IPv4 address or Hostname.


  eradicate (optional, bool, no)
    Define whether to eradicate the snapshot on delete or leave in trash.


  state (optional, str, present)
    Define whether the protection group snapshot should exist or not. Copy (added in 2.7) will create a full read/write clone of the snapshot.


  target (optional, str, None)
    Volume to restore a specified volume to.

    If not supplied this will default to the volume defined in *restore*


  remote (optional, bool, False)
    Force immeadiate snapshot to remote targets


  now (optional, bool, False)
    Whether to initiate a snapshot of the protection group immeadiately


  overwrite (optional, bool, no)
    Define whether to overwrite the target volume if it already exists.


  suffix (optional, str, None)
    Suffix of snapshot name.

    Special case. If *latest* the module will select the latest snapshot created in the group




Notes
-----

.. note::
   - This module requires the ``purestorage`` Python library
   - You must set ``PUREFA_URL`` and ``PUREFA_API`` environment variables if *fa_url* and *api_token* arguments are not passed to the module directly




Examples
--------

.. code-block:: yaml+jinja

    
    - name: Create protection group snapshot foo.ansible
      purefa_pgsnap:
        name: foo
        suffix: ansible
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: present
    
    - name: Delete and eradicate protection group snapshot named foo.snap
      purefa_pgsnap:
        name: foo
        suffix: snap
        eradicate: true
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: absent
    
    - name: Restore volume data from local protection group snapshot named foo.snap to volume data2
      purefa_pgsnap:
        name: foo
        suffix: snap
        restore: data
        target: data2
        overwrite: true
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: copy
    
    - name: Restore remote protection group snapshot arrayA:pgname.snap.data to local copy
      purefa_pgsnap:
        name: arrayA:pgname
        suffix: snap
        restore: data
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: copy
    
    - name: Create snapshot of existing pgroup foo with suffix and force immeadiate copy to remote targets
      purefa_pgsnap:
        name: pgname
        suffix: force
        now: True
        apply_retention: True
        remote: True
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: copy
    
    - name: Delete and eradicate snapshot named foo.snap on offload target bar from arrayA
      purefa_pgsnap:
        name: "arrayA:foo"
        suffix: snap
        offload: bar
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

