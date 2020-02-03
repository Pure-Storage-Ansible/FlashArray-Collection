
purefa_subnet -- Manage network subnets in a Pure Storage FlashArray
====================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

This module manages the network subnets on a Pure Storage FlashArray.



Requirements
------------
The below requirements are needed on the host that executes this module.

- netaddr
- purestorage
- python >= 2.7



Parameters
----------

  fa_url (True, str, None)
    FlashArray management IPv4 address or Hostname.


  prefix (False, str, None)
    Set the IPv4 or IPv6 address to be associated with the subnet.


  gateway (False, str, None)
    IPv4 or IPv6 address of subnet gateway.


  name (True, str, None)
    Subnet name.


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  vlan (False, int, None)
    VLAN ID. Range is 0 to 4094.


  enabled (optional, bool, True)
    whether the subnet should be enabled or not


  state (False, str, present)
    Create or delete subnet.


  mtu (False, int, 1500)
    MTU size of the subnet. Range is 568 to 9000.





Notes
-----

.. note::
   - Requires the netaddr Python package on the host.
   - This module requires the ``purestorage`` Python library
   - You must set ``PUREFA_URL`` and ``PUREFA_API`` environment variables if *fa_url* and *api_token* arguments are not passed to the module directly




Examples
--------

.. code-block:: yaml+jinja

    
    - name: Create subnet subnet100
      purefa_subnet:
        name: subnet100
        vlan: 100
        gateway: 10.21.200.1
        prefix: "10.21.200.0/24"
        mtu: 9000
        state: present
        fa_url: 10.10.10.2
        api_token: c6033033-fe69-2515-a9e8-966bb7fe4b40
    
    - name: Disable subnet subnet100
      purefa_subnet:
        name: subnet100
        enabled: false
        fa_url: 10.10.10.2
        api_token: c6033033-fe69-2515-a9e8-966bb7fe4b40
    
    - name: Delete subnet subnet100
      purefa_subnet:
        name: subnet100
        state: absent
        fa_url: 10.10.10.2
        api_token: c6033033-fe69-2515-a9e8-966bb7fe4b40




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

