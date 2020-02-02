
purefa_vnc -- Enable or Disable VNC port for installed apps
===========================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Enablke or Disable VNC access for installed apps



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  state (optional, str, present)
    Define state of VNC


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  name (True, str, None)
    Name od app


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

    
    - name: Enable VNC for application test
      purefa_vnc:
        name: test
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Disable VNC for application test
      purefa_vnc:
        name: test
        state: absent
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592


Return Values
-------------

  vnc (success, dict, )
    VNC port information for application

    status (, str, healthy)
      Status of application

    index (, int, )
      Application index number

    version (, str, 5.2.1)
      Application version installed

    vnc (, dict, ['10.21.200.34:5900'])
      IP address and port number for VNC connection

    name (, str, )
      Application name





Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

