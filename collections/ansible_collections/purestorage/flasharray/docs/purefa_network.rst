
purefa_network -- Manage network interfaces in a Pure Storage FlashArray
========================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

This module manages the physical and virtual network interfaces on a Pure Storage FlashArray.

To manage VLAN interfaces use the *purefa_vlan* module.

To manage network subnets use the *purefa_subnet* module.

To remove an IP address from a non-management port use 0.0.0.0/0



Requirements
------------
The below requirements are needed on the host that executes this module.

- netaddr
- purestorage
- python >= 2.7



Parameters
----------

  name (True, str, None)
    Interface name (physical or virtual).


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  mtu (False, int, 1500)
    MTU size of the interface. Range is 1280 to 9216.


  state (False, str, present)
    State of existing interface (on/off).


  address (False, str, None)
    IPv4 or IPv6 address of interface in CIDR notation.

    To remove an IP address from a non-management port use 0.0.0.0/0


  gateway (False, str, None)
    IPv4 or IPv6 address of interface gateway.


  fa_url (True, str, None)
    FlashArray management IPv4 address or Hostname.





Notes
-----

.. note::
   - Requires the netaddr Python package on the host.
   - This module requires the ``purestorage`` Python library
   - You must set ``PUREFA_URL`` and ``PUREFA_API`` environment variables if *fa_url* and *api_token* arguments are not passed to the module directly




Examples
--------

.. code-block:: yaml+jinja

    
    - name: Configure and enable network interface ct0.eth8
      purefa_network:
        name: ct0.eth8
        gateway: 10.21.200.1
        address: "10.21.200.18/24"
        mtu: 9000
        state: present
        fa_url: 10.10.10.2
        api_token: c6033033-fe69-2515-a9e8-966bb7fe4b40
    
    - name: Disable physical interface ct1.eth2
      purefa_network:
        name: ct1.eth2
        state: absent
        fa_url: 10.10.10.2
        api_token: c6033033-fe69-2515-a9e8-966bb7fe4b40
    
    - name: Enable virtual network interface vir0
      purefa_network:
        name: vir0
        state: present
        fa_url: 10.10.10.2
        api_token: c6033033-fe69-2515-a9e8-966bb7fe4b40
    
    - name: Remove an IP address from iSCSI interface ct0.eth4
      purefa_network:
        name: ct0.eth4
        address: 0.0.0.0/0
        gateway: 0.0.0.0
        fa_url: 10.10.10.2
        api_token: c6033033-fe69-2515-a9e8-966bb7fe4b40




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

