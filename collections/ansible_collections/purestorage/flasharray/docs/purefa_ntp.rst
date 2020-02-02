
purefa_ntp -- Configure Pure Storage FlashArray NTP settings
============================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Set or erase NTP configuration for Pure Storage FlashArrays.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  ntp_servers (optional, list, None)
    A list of up to 4 alternate NTP servers. These may include IPv4, IPv6 or FQDNs. Invalid IP addresses will cause the module to fail. No validation is performed for FQDNs.

    If more than 4 servers are provided, only the first 4 unique nameservers will be used.

    if no servers are given a default of *0.pool.ntp.org* will be used.


  state (optional, str, present)
    Create or delete NTP servers configuration


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

    
    - name: Delete exisitng NTP server entries
      purefa_ntp:
        state: absent
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Set array NTP servers
      purefa_ntp:
        state: present
        ntp_servers:
          - "0.pool.ntp.org"
          - "1.pool.ntp.org"
          - "2.pool.ntp.org"
          - "3.pool.ntp.org"
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

