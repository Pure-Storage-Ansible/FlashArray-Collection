
purefa_alert -- Configure Pure Storage FlashArray alert email settings
======================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Configure alert email configuration for Pure Storage FlashArrays.

Add or delete an individual syslog server to the existing list of serves.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  state (optional, str, present)
    Create or delete alert email


  fa_url (True, str, None)
    FlashArray management IPv4 address or Hostname.


  enabled (optional, bool, True)
    Set specified email address to be enabled or disabled


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  address (True, str, None)
    Email address (valid format required)





Notes
-----

.. note::
   - This module requires the ``purestorage`` Python library
   - You must set ``PUREFA_URL`` and ``PUREFA_API`` environment variables if *fa_url* and *api_token* arguments are not passed to the module directly




Examples
--------

.. code-block:: yaml+jinja

    
    - name: Add new email recipient and enable, or enable existing email
      purefa_alert:
        address: "user@domain.com"
        enabled: true
        state: present
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    - name: Delete existing email recipient
      purefa_alert:
        state: absent
        address: "user@domain.com"
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Simon Dodsley (@sdodsley)

