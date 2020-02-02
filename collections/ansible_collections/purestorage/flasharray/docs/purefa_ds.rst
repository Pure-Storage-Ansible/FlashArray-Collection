
purefa_ds -- Configure FlashArray Directory Service
===================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Set or erase configuration for the directory service. There is no facility to SSL certificates at this time. Use the FlashArray GUI for this additional configuration work.

To modify an existing directory service configuration you must first delete an exisitng configuration and then recreate with new settings.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  bind_user (optional, str, None)
    Sets the user name that can be used to bind to and query the directory.

    For Active Directory, enter the username - often referred to as sAMAccountName or User Logon Name - of the account that is used to perform directory lookups.

    For OpenLDAP, enter the full DN of the user.


  group_base (optional, str, None)
    Specifies where the configured groups are located in the directory tree. This field consists of Organizational Units (OUs) that combine with the base DN attribute and the configured group CNs to complete the full Distinguished Name of the groups. The group base should specify OU= for each OU and multiple OUs should be separated by commas. The order of OUs is important and should get larger in scope from left to right. Each OU should not exceed 64 characters in length.

    Not Supported from Purity 5.2.0 or higher. Use *purefa_dsrole* module.


  enable (optional, bool, False)
    Whether to enable or disable directory service support.


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  uri (optional, list, None)
    A list of up to 30 URIs of the directory servers. Each URI must include the scheme ldap:// or ldaps:// (for LDAP over SSL), a hostname, and a domain name or IP address. For example, ldap://ad.company.com configures the directory service with the hostname "ad" in the domain "company.com" while specifying the unencrypted LDAP protocol.


  aa_group (optional, str, None)
    Sets the common Name (CN) of the directory service group containing administrators with full privileges when managing the FlashArray. The name should be just the Common Name of the group without the CN= specifier. Common Names should not exceed 64 characters in length.

    Not Supported from Purity 5.2.0 or higher. Use *purefa_dsrole* module.


  ro_group (optional, str, None)
    Sets the common Name (CN) of the configured directory service group containing users with read-only privileges on the FlashArray. This name should be just the Common Name of the group without the CN= specifier. Common Names should not exceed 64 characters in length.

    Not Supported from Purity 5.2.0 or higher. Use *purefa_dsrole* module.


  state (optional, str, present)
    Create or delete directory service configuration


  bind_password (optional, str, None)
    Sets the password of the bind_user user name account.


  base_dn (True, str, None)
    Sets the base of the Distinguished Name (DN) of the directory service groups. The base should consist of only Domain Components (DCs). The base_dn will populate with a default value when a URI is entered by parsing domain components from the URI. The base DN should specify DC= for each domain component and multiple DCs should be separated by commas.


  sa_group (optional, str, None)
    Sets the common Name (CN) of the configured directory service group containing administrators with storage-related privileges on the FlashArray. This name should be just the Common Name of the group without the CN= specifier. Common Names should not exceed 64 characters in length.

    Not Supported from Purity 5.2.0 or higher. Use *purefa_dsrole* module.


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

    
    - name: Delete existing directory service
      purefa_ds:
        state: absent
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Create directory service (disabled) - Pre-5.2.0
      purefa_ds:
        uri: "ldap://lab.purestorage.com"
        base_dn: "DC=lab,DC=purestorage,DC=com"
        bind_user: Administrator
        bind_password: password
        group_base: "OU=Pure-Admin"
        ro_group: PureReadOnly
        sa_group: PureStorage
        aa_group: PureAdmin
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Create directory service (disabled) - 5.2.0 or higher
      purefa_ds:
        uri: "ldap://lab.purestorage.com"
        base_dn: "DC=lab,DC=purestorage,DC=com"
        bind_user: Administrator
        bind_password: password
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Enable existing directory service
      purefa_ds:
        enable: true
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Disable existing directory service
      purefa_ds:
        enable: false
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Create directory service (enabled) - Pre-5.2.0
      purefa_ds:
        enable: true
        uri: "ldap://lab.purestorage.com"
        base_dn: "DC=lab,DC=purestorage,DC=com"
        bind_user: Administrator
        bind_password: password
        group_base: "OU=Pure-Admin"
        ro_group: PureReadOnly
        sa_group: PureStorage
        aa_group: PureAdmin
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Create directory service (enabled) - 5.2.0 or higher
      purefa_ds:
        enable: true
        uri: "ldap://lab.purestorage.com"
        base_dn: "DC=lab,DC=purestorage,DC=com"
        bind_user: Administrator
        bind_password: password
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

