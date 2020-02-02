
purefa_vlan -- Manage network VLAN interfaces in a Pure Storage FlashArray
==========================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

This module manages the VLAN network interfaces on a Pure Storage FlashArray.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  subnet (True, str, None)
    Name of subnet interface associated with.


  name (True, str, None)
    Interface name, including controller indentifier.

    VLANs are only supported on iSCSI physical interfaces


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  enabled (False, bool, True)
    Define if VLAN interface is enabled or not.


  state (False, str, present)
    State of existing interface (on/off).


  address (False, str, None)
    IPv4 or IPv6 address of interface.


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

    
    - name: Configure and enable VLAN interface ct0.eth8 for subnet test
      purefa_vlan:
        name: ct0.eth8
        subnet: test
        address: 10.21.200.18
        state: present
        fa_url: 10.10.10.2
        api_token: c6033033-fe69-2515-a9e8-966bb7fe4b40
    
    - name: Disable VLAN interface for subnet test on ct1.eth2
      purefa_vlan:
        name: ct1.eth2
        subnet: test
        enabled: false
        fa_url: 10.10.10.2
        api_token: c6033033-fe69-2515-a9e8-966bb7fe4b40
    
    - name: Delete VLAN inteface for subnet test on ct0.eth4
      purefa_vlan:
        name: ct0.eth4
        subnet: test
        state: absent
        fa_url: 10.10.10.2
        api_token: c6033033-fe69-2515-a9e8-966bb7fe4b40




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- P
- u
- r
- e
-  
- S
- t
- o
- r
- a
- g
- e
-  
- A
- n
- s
- i
- b
- l
- e
-  
- T
- e
- a
- m
-  
- (
- @
- s
- d
- o
- d
- s
- l
- e
- y
- )
-  
- <
- p
- u
- r
- e
- -
- a
- n
- s
- i
- b
- l
- e
- -
- t
- e
- a
- m
- @
- p
- u
- r
- e
- s
- t
- o
- r
- a
- g
- e
- .
- c
- o
- m
- >

