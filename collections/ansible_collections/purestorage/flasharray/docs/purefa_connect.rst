
purefa_connect -- Manage replication connections between two FlashArrays
========================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Manage array connections to specified target array



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  target_url (True, str, None)
    Management IP address of remote array.


  target_api (optional, str, None)
    API token for target array


  connection (optional, str, async)
    T

    y

    p

    e

     

    o

    f

     

    c

    o

    n

    n

    e

    c

    t

    i

    o

    n

     

    b

    e

    t

    w

    e

    e

    n

     

    a

    r

    r

    a

    y

    s

    .


  state (optional, str, present)
    Create or delete array connection


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

    
    - name: Create an async connection to remote array
      purefa_connect:
        target_url: 10.10.10.20
        target_api: 9c0b56bc-f941-f7a6-9f85-dcc3e9a8f7d6
        connection: async
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    - name: Delete connection to remote array
      purefa_connect:
        state: absent
        target_url: 10.10.10.20
        target_api: 9c0b56bc-f941-f7a6-9f85-dcc3e9a8f7d6
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

