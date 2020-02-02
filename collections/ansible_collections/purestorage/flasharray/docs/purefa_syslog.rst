
purefa_syslog -- Configure Pure Storage FlashArray syslog settings
==================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Configure syslog configuration for Pure Storage FlashArrays.

Add or delete an individual syslog server to the existing list of serves.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  protocol (True, str, None)
    Protocol which server uses


  address (True, str, None)
    Syslog server address. This field supports IPv4, IPv6 or FQDN. An invalid IP addresses will cause the module to fail. No validation is performed for FQDNs.


  state (optional, str, present)
    Create or delete syslog servers configuration


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  port (optional, str, None)
    Port at which the server is listening. If no port is specified the system will use 514


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

    
    - name: Delete exisitng syslog server entries
      purefa_syslog:
        address: syslog1.com
        protocol: tcp
        state: absent
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Set array syslog servers
      purefa_syslog:
        state: present
        address: syslog1.com
        protocol: udp
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

