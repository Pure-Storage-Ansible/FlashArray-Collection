
purefa_proxy -- Configure FlashArray phonehome HTTPs proxy settings
===================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Set or erase configuration for the HTTPS phonehome proxy settings.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  state (optional, str, present)
    Set or delete proxy configuration


  fa_url (True, str, None)
    FlashArray management IPv4 address or Hostname.


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  host (optional, str, None)
    The proxy host name.


  port (optional, int, None)
    The proxy TCP/IP port number.





Notes
-----

.. note::
   - This module requires the ``purestorage`` Python library
   - You must set ``PUREFA_URL`` and ``PUREFA_API`` environment variables if *fa_url* and *api_token* arguments are not passed to the module directly




Examples
--------

.. code-block:: yaml+jinja

    
    - name: Delete exisitng proxy settings
      purefa_proxy:
        state: absent
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Set proxy settings
      purefa_proxy:
        host: purestorage.com
        port: 8080
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

