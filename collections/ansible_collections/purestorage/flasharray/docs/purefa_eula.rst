
purefa_eula -- Sign Pure Storage FlashArray EULA
================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Sign the FlashArray EULA for Day 0 config, or change signatory.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  company (True, str, None)
    Full legal name of the entity.

    The value must be between 1 and 64 characters in length.


  fa_url (True, str, None)
    FlashArray management IPv4 address or Hostname.


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  name (True, str, None)
    Full legal name of the individual at the company who has the authority to accept the terms of the agreement.

    The value must be between 1 and 64 characters in length.


  title (True, str, None)
    Individual's job title at the company.

    The value must be between 1 and 64 characters in length.





Notes
-----

.. note::
   - This module requires the ``purestorage`` Python library
   - You must set ``PUREFA_URL`` and ``PUREFA_API`` environment variables if *fa_url* and *api_token* arguments are not passed to the module directly




Examples
--------

.. code-block:: yaml+jinja

    
    - name: Sign EULA for FlashArrayt
      purefa_eula:
        company: "ACME Storage, Inc."
        name: "Fred Bloggs"
        title: "Storage Manager"
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

