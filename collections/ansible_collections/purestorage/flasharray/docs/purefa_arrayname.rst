
purefa_arrayname -- Configure Pure Storage FlashArray array name
================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Configure name of array for Pure Storage FlashArrays.

Ideal for Day 0 initial configuration.



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

     

    t

    h

    e

     

    a

    r

    r

    a

    y

     

    n

    a

    m

    e


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  name (True, str, None)
    Name of the array. Must conform to correct naming schema.


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

    
    - name: Set new array name
      purefa_arrayname:
        name: new-array-name
        state: present
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

