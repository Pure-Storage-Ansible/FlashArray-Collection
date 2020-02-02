
purefa_banner -- Configure Pure Storage FlashArray GUI and SSH MOTD message
===========================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Configure MOTD for Pure Storage FlashArrays.

This will be shown during an SSH or GUI login to the array.

Multiple line messages can be achieved using \\n.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  state (optional, str, present)
    S

    e

    t

     

    o

    t

     

    d

    e

    l

    e

    t

    e

     

    t

    h

    e

     

    M

    O

    T

    D


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  banner (optional, str, Welcome to the machine...)
    B

    a

    n

    n

    e

    r

     

    t

    e

    x

    t

    ,

     

    o

    r

     

    M

    O

    T

    D

    ,

     

    t

    o

     

    u

    s

    e


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

    
    - name: Set new banner text
      purefa_banner:
        banner: "Banner over\ntwo lines"
        state: present
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Delete banner text
      purefa_banner:
        state: absent
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

