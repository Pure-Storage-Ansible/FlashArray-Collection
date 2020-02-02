
purefa_endpoint -- Manage VMware protocol-endpoints on Pure Storage FlashArrays
===============================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Create, delete or eradicate the an endpoint on a Pure Storage FlashArray.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  rename (optional, str, None)
    Value to rename the specified endpoint to.

    Rename only applies to the container the current endpoint is in.


  host (optional, str, None)
    name of host to attach endpoint to


  name (True, str, None)
    The name of the endpoint.


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  eradicate (optional, bool, no)
    Define whether to eradicate the endpoint on delete or leave in trash.


  fa_url (True, str, None)
    FlashArray management IPv4 address or Hostname.


  state (optional, str, present)
    Define whether the endpoint should exist or not.


  hgroup (optional, str, None)
    name of hostgroup to attach endpoint to





Notes
-----

.. note::
   - This module requires the ``purestorage`` Python library
   - You must set ``PUREFA_URL`` and ``PUREFA_API`` environment variables if *fa_url* and *api_token* arguments are not passed to the module directly




Examples
--------

.. code-block:: yaml+jinja

    
    - name: Create new endpoint named foo
      purefa_endpoint:
        name: test-endpoint
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: present
    
    - name: Delete and eradicate endpoint named foo
      purefa_endpoint:
        name: foo
        eradicate: yes
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: absent
    
    - name: Rename endpoint foor to bar
      purefa_endpoint:
        name: foo
        rename: bar
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592


Return Values
-------------

  volume (success, dict, )
    A dictionary describing the changed volume.  Only some attributes below will be returned with various actions.

    source (, str, )
      Volume name of source volume used for volume copy

    serial (, str, 361019ECACE43D83000120A4)
      Volume serial number

    name (, str, )
      Volume name

    created (, str, 2019-03-13T22:49:24Z)
      Volume creation time





Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

