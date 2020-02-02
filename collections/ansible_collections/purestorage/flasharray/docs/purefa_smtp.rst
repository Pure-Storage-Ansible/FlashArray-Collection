
purefa_smtp -- Configure FlashArray SMTP settings
=================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Set or erase configuration for the SMTP settings.

If username/password are set this will always force a change as there is no way to see if the password is differnet from the current SMTP configuration.

Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  sender_domain (optional, str, None)
    Domain name.


  state (optional, str, present)
    Set or delete SMTP configuration


  user (optional, str, None)
    The SMTP username.


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  password (optional, str, None)
    The SMTP password.


  relay_host (optional, str, None)
    IPv4 or IPv6 address or FQDN. A port number may be appended.


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

    
    - name: Delete exisitng SMTP settings
      purefa_smtp:
        state: absent
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    - name: Set SMTP settings
      purefa_smtp:
        sender_domain: purestorage.com
        password: account_password
        user: smtp_account
        relay_host: 10.2.56.78:2345
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

