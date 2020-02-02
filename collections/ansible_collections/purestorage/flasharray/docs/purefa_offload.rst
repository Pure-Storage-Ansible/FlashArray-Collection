
purefa_offload -- Create, modify and delete NFS, S3 or Azure offload targets
============================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Create, modify and delete NFS, S3 or Azure offload targets.

Only supported on Purity v5.2.0 or higher.

You must have a correctly configured offload network for offload to work.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  access_key (optional, str, None)
    Access Key ID of the S3 target


  account (optional, str, None)
    Name of the Azure blob storage account


  protocol (optional, str, nfs)
    Define which protocol the offload engine uses


  name (True, str, None)
    The name of the offload target


  share (optional, str, None)
    NFS export on the NFS server


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  bucket (optional, str, None)
    Name of the bucket for the S3 target


  state (optional, str, present)
    Define state of offload


  secret (optional, str, None)
    Secret Access Key for the S3 or Azure target


  container (optional, str, offload)
    Name of the blob container of the Azure target


  address (optional, str, None)
    The IP or FQDN address of the NFS server


  initialize (optional, bool, True)
    Define whether to initialize the S3 bucket


  placement (optional, str, retention-based)
    AWS S3 placement strategy


  options (False, str, )
    Additonal mount options for the NFS share

    Supported mount options include *port*, *rsize*, *wsize*, *nfsvers*, and *tcp* or *udp*


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

    
    - name: Create NFS offload target
      purefa_offload:
        name: nfs-offload
        protocol: nfs
        address: 10.21.200.4
        share: "/offload_target"
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Create S3 offload target
      purefa_offload:
        name: s3-offload
        protocol: s3
        access_key: "3794fb12c6204e19195f"
        bucket: offload-bucket
        secret: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        placement: aws-standard-class
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Create Azure offload target
      purefa_offload:
        name: azure-offload
        protocol: azure
        secret: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        container: offload-container
        account: user1
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Delete offload target
      purefa_offload:
        name: nfs-offload
        protocol: nfs
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

