
purefa_user -- Create, modify or delete FlashArray local user account
=====================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Create, modify or delete local users on a Pure Stoage FlashArray.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  state (optional, str, present)
    Create, delete or update local user account


  api (optional, bool, False)
    Define whether to create an API token for this user

    Token can be exposed using the *debug* module


  role (optional, str, None)
    Sets the local user's access level to the array


  name (optional, str, None)
    The name of the local user account


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  password (optional, str, None)
    Password for the local user.


  old_password (optional, str, None)
    If changing an existing password, you must provide the old password for security


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

    
    - name: Create new user ansible with API token
      purefa_user:
        name: ansible
        password: apassword
        role: storage_admin
        api: true
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
      register: result
    
      debug:
        msg: "API Token: {{ result['user_info']['user_api'] }}"
    
    - name: Change role type for existing user
      purefa_user:
        name: ansible
        role: array_admin
        state: update
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Change password type for existing user (NOT IDEMPOTENT)
      purefa_user:
        name: ansible
        password: anewpassword
        old_password: apassword
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Change API token for existing user
      purefa_user:
        name: ansible
        api: true
        state: update
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
      register: result
    
      debug:
        msg: "API Token: {{ result['user_info']['user_api'] }}"




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

