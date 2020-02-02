
purefa_console -- Enable or Disable Pure Storage FlashArray Console Lock
========================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Enablke or Disable root lockout from the array at the physical console for a Pure Storage FlashArray.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  state (optional, str, disable)
    Define state of console lockout

    When set to *enable* the console port is locked from root login.


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

    
    - name: Enable Console Lockout
      purefa_console:
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Disable Console Lockout
      purefa_console:
        state: disable
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

