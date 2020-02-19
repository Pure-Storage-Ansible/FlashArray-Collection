
purefa_timeout -- Configure Pure Storage FlashArray GUI idle timeout
====================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Configure GUI idle timeout for Pure Storage FlashArrays.

This does not affect existing GUI sessions.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  state (optional, str, present)
    Set or disable the GUI idle timeout


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  timeout (optional, int, 30)
    Minutes for idle timeout.


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

    
    - name: Set GUI idle timeout to 25 minutes
      purefa_gui:
        timeout: 25
        state: present
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Disable idle timeout
      purefa_gui:
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

