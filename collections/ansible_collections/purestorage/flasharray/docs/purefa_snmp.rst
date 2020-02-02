
purefa_snmp -- Configure FlashArray SNMP Managers
=================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Manage SNMP managers on a Pure Storage FlashArray.

Changing of a named SNMP managers version is not supported.

This module is not idempotent and will always modify an existing SNMP manager due to hidden parameters that cannot be compared to the play parameters.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  name (True, str, None)
    Name of SNMP Manager


  notification (optional, str, trap)
    Action to perform on event.


  state (optional, str, present)
    Create or delete SNMP manager


  community (optional, str, None)
    SNMP v2c only. Manager community ID. Between 1 and 32 characters long.


  privacy_protocol (optional, str, None)
    SNMP v3 only. Encryption protocol to use


  auth_protocol (optional, str, None)
    SNMP v3 only. Hash algorithm to use


  host (True, str, None)
    IPv4 or IPv6 address or FQDN to send trap messages to.


  version (optional, str, v2c)
    Version of SNMP protocol to use for the manager.


  user (optional, str, None)
    SNMP v3 only. User ID recognized by the specified SNMP manager. Must be between 1 and 32 characters.


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  privacy_passphrase (optional, str, None)
    SNMPv3 only. Passphrase to encrypt SNMP messages. Must be between 8 and 63 non-space ASCII characters.


  auth_passphrase (optional, str, None)
    SNMPv3 only. Passphrase of 8 - 32 characters.


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

    
    - name: Delete exisitng SNMP manager
      purefa_snmp:
        name: manager1
        state: absent
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    - name: Create v2c SNMP manager
      purefa_snmp:
        name: manager1
        community: public
        host: 10.21.22.23
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    - name: Create v3 SNMP manager
      purefa_snmp:
        name: manager2
        version: v3
        auth_protocol: MD5
        auth_passphrase: password
        host: 10.21.22.23
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    - name: Update existing SNMP manager
      purefa_snmp:
        name: manager1
        community: private
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

