
purefa_dns -- Configure FlashArray DNS settings
===============================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Set or erase configuration for the DNS settings.

Nameservers provided will overwrite any existing nameservers.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  nameservers (optional, list, None)
    List of up to 3 unique DNS server IP addresses. These can be IPv4 or IPv6 - No validation is done of the addresses is performed.


  state (optional, str, present)
    Set or delete directory service configuration


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  domain (optional, str, None)
    Domain suffix to be appended when perofrming DNS lookups.


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

    
    - name: Delete exisitng DNS settings
      purefa_dns:
        state: absent
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Set DNS settings
      purefa_dns:
        domain: purestorage.com
        nameservers:
          - 8.8.8.8
          - 8.8.4.4
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

