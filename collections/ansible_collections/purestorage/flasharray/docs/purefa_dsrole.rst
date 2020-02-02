
purefa_dsrole -- Configure FlashArray Directory Service Roles
=============================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Set or erase directory services role configurations.

Only available for FlashArray running Purity 5.2.0 or higher



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  group_base (optional, str, None)
    Specifies where the configured group is located in the directory tree. This field consists of Organizational Units (OUs) that combine with the base DN attribute and the configured group CNs to complete the full Distinguished Name of the groups. The group base should specify OU= for each OU and multiple OUs should be separated by commas. The order of OUs is important and should get larger in scope from left to right.

    Each OU should not exceed 64 characters in length.


  group (optional, str, None)
    Sets the common Name (CN) of the configured directory service group containing users for the FlashBlade. This name should be just the Common Name of the group without the CN= specifier.

    Common Names should not exceed 64 characters in length.


  state (optional, str, present)
    Create or delete directory service role


  role (optional, str, None)
    The directory service role to work on


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

    
    - name: Delete exisitng array_admin directory service role
      purefa_dsrole:
        role: array_admin
        state: absent
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Create array_admin directory service role
      purefa_dsrole:
        role: array_admin
        group_base: "OU=PureGroups,OU=SANManagers"
        group: pureadmins
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Update ops_admin directory service role
      purefa_dsrole:
        role: ops_admin
        group_base: "OU=PureGroups"
        group: opsgroup
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

