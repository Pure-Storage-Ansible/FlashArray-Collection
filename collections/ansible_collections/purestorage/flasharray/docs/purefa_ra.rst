
purefa_ra -- Enable or Disable Pure Storage FlashArray Remote Assist
====================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Enablke or Disable Remote Assist for a Pure Storage FlashArray.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  state (optional, str, enable)
    Define state of remote assist

    When set to *enable* the RA port can be exposed using the *debug* module.


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

    
    - name: Enable Remote Assist port
      purefa_ra:
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
      register: result
    
      debug:
        msg: "Remote Assist: {{ result['ra_facts'] }}"
    
    - name: Disable Remote Assist port
      purefa_ra:
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

