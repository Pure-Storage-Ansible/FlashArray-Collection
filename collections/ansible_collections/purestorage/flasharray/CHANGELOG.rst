====================================
Purestorage.Flasharray Release Notes
====================================

.. contents:: Topics


v1.11.0
=======

Minor Changes
-------------

- purefa_host - Deprecate ``protocol`` parameter. No longer required.
- purefa_info - Add NVMe NGUID value for volumes
- purefa_info - Add array, volume and snapshot detailed capacity information
- purefa_info - Add deleted members to volume protection group info
- purefa_info - Add snapshot policy rules suffix support
- purefa_info - Remove directory_services field. Deprecated in Collections 1.6
- purefa_policy - Add snapshot policy rules suffix support
- purefa_syslog_settings - Add support to manage global syslog server settings
- purefa_volume - Add NVMe NGUID to response dict

Bugfixes
--------

- purefa_subnet - Add regex to check for correct dsubnet name
- purefa_user - Add regex to check for correct username

v1.10.0
=======

Minor Changes
-------------

- purefa_ds - Add ``join_ou`` parameter for AD account creation
- purefa_kmip - Add support for KMIP server management

New Modules
-----------

- purestorage.flasharray.purefa_kmip - Manage FlashArray KMIP server objects

v1.9.0
======

Minor Changes
-------------

- purefa_ad - Increase number of kerberos and directory servers to be 3 for each.
- purefa_ad - New module to manage Active Directory accounts
- purefa_dirsnap - New modules to manage FA-Files directory snapshots
- purefa_eradication - New module to set deleted items eradication timer
- purefa_info - Add data-at-rest and eradication timer information to default dict
- purefa_info - Add high-level count for directory quotas and details for all FA-Files policies
- purefa_info - Add volume Page 83 NAA information for volume details
- purefa_network - Add support for enable/diable FC ports
- purefa_policy - Add support for FA-files Directory Quotas and associated rules and members
- purefa_sso - Add support for setting FlashArray Single Sign-On from Pure1 Manage
- purefa_volume - Add volume Page 83 NAA information to response dict

Bugfixes
--------

- purefa_host - Rollback host creation if initiators already used by another host
- purefa_policy - Fix incorrect protocol endpoint invocation
- purefa_ra - fix disable feature for remote assist, this didn't work due to error in check logic
- purefa_vg - Correct issue when setting or changing Volume Group QoS
- purefa_volume - Fix incorrect API version check for ActiveDR support

New Modules
-----------

- purestorage.flasharray.purefa_ad - Manage FlashArray Active Directory Account
- purestorage.flasharray.purefa_dirsnap - Manage FlashArray File System Directory Snapshots
- purestorage.flasharray.purefa_eradication - Configure Pure Storage FlashArray Eradication Timer
- purestorage.flasharray.purefa_sso - Configure Pure Storage FlashArray Single Sign-On

v1.8.0
======

Minor Changes
-------------

- purefa_certs - New module for managing SSL certificates
- purefa_volume - New parameter pgroup to specify an existing protection group to put crwated volume(s) in.

Bugfixes
--------

- purefa_dsrole - If using None for group or group_base incorrect change state applied
- purefa_network - Allow gateway paremeter to be set as None - needed for non-routing iSCSI ports
- purefa_pg - Check to ensure protection group name meets naming convention
- purefa_pgsnap - Fail with warning if trying to restore to a stretched ActiveCluster pod
- purefa_volume - Ensure REST version is high enough to support promotion_status

New Modules
-----------

- purestorage.flasharray.purefa_certs - Manage FlashArray SSL Certificates

v1.7.0
======

Minor Changes
-------------

- purefa_maintenance - New module to set maintenance windows
- purefa_pg - Add support to rename protection groups
- purefa_syslog - Add support for naming SYSLOG servers for Purity//FA 6.1 or higher

Bugfixes
--------

- purefa_info - Fix missing protection group snapshot info for local snapshots
- purefa_info - Resolve crash when an offload target is offline
- purefa_pgsnap - Ensure suffix rules only implemented for state=present
- purefa_user - Do not allow role changed for breakglass user (pureuser)
- purefa_user - Do not change role for existing user unless requested

New Modules
-----------

- purestorage.flasharray.purefa_maintenance - Configure Pure Storage FlashArray Maintence Windows

v1.6.2
======

Bugfixes
--------

- purefa_volume - Fix issues with moving volumes into demoted or linked pods

v1.6.0
======

Minor Changes
-------------

- purefa_connect - Add support for FC-based array replication
- purefa_ds - Add Purity v6 support for Directory Services, including Data DS and updating services
- purefa_info - Add support for FC Replication
- purefa_info - Add support for Remote Volume Snapshots
- purefa_info - Update directory_services dictionary to cater for FA-Files data DS. Change DS dict forward. Add deprecation warning.
- purefa_ntp - Ignore NTP configuration for CBS-based arrays
- purefa_pg - Add support for Protection Groups in AC pods
- purefa_snap - Add support for remote snapshot of individual volumes to offload targets

Bugfixes
--------

- purefa_hg - Ensure all hostname chacks are lowercase for consistency
- purefa_pgsnap - Add check to ensure suffix name meets naming conventions
- purefa_pgsnap - Ensure pgsnap restores work for AC PGs
- purefa_pod - Ensure all pod names are lowercase for consistency
- purefa_snap - Update suffix regex pattern
- purefa_volume - Add missing variable initialization

v1.5.1
======

Minor Changes
-------------

- purefa_host - Add host rename function
- purefa_host - Add support for multi-host creation
- purefa_vg - Add support for multiple vgroup creation
- purefa_volume - Add support for multi-volume creation

Bugfixes
--------

- purefa.py - Resolve issue when pypureclient doesn't handshake array correctly
- purefa_dns - Fix idempotency
- purefa_volume - Alert when volume selected for move does not exist

v1.5.0
======

Minor Changes
-------------

- purefa_apiclient - New module to support API Client management
- purefa_directory - Add support for managed directories
- purefa_export - Add support for filesystem exports
- purefa_fs - Add filesystem management support
- purefa_hg - Enforce case-sensitivity rules for hostgroup objects
- purefa_host - Enforce hostname case-sensitivity rules
- purefa_info - Add support for FA Files features
- purefa_offload - Add support for Google Cloud offload target
- purefa_pg - Enforce case-sensitivity rules for protection group objects
- purefa_policy - Add support for NFS, SMB and Snapshot policy management

Bugfixes
--------

- purefa_host - Correctly remove host that is in a hostgroup
- purefa_volume - Fix failing idempotency on eradicate volume

New Modules
-----------

- purestorage.flasharray.purefa_apiclient - Manage FlashArray API Clients
- purestorage.flasharray.purefa_directory - Manage FlashArray File System Directories
- purestorage.flasharray.purefa_export - Manage FlashArray File System Exports
- purestorage.flasharray.purefa_fs - Manage FlashArray File Systems
- purestorage.flasharray.purefa_policy - Manage FlashArray File System Policies

v1.4.0
======

Release Summary
---------------

| Release Date: 2020-08-08
| This changlelog describes all changes made to the modules and plugins included in this collection since Ansible 2.9.0


Major Changes
-------------

- purefa_console - manage Console Lock setting for the FlashArray
- purefa_endpoint - manage VMware protocol-endpoints on the FlashArray
- purefa_eula - sign, or resign, FlashArray EULA
- purefa_inventory - get hardware inventory information from a FlashArray
- purefa_network - manage the physical and virtual network settings on the FlashArray
- purefa_pgsched - manage protection group snapshot and replication schedules on the FlashArray
- purefa_pod - manage ActiveCluster pods in FlashArrays
- purefa_pod_replica - manage ActiveDR pod replica links in FlashArrays
- purefa_proxy - manage the phonehome HTTPS proxy setting for the FlashArray
- purefa_smis - manage SMI-S settings on the FlashArray
- purefa_subnet - manage network subnets on the FlashArray
- purefa_timeout - manage the GUI idle timeout on the FlashArray
- purefa_vlan - manage VLAN interfaces on the FlashArray
- purefa_vnc - manage VNC for installed applications on the FlashArray
- purefa_volume_tags - manage volume tags on the FlashArray

Minor Changes
-------------

- purefa_hg - All LUN ID to be set for single volume
- purefa_host - Add CHAP support
- purefa_host - Add support for Cloud Block Store
- purefa_host - Add volume disconnection support
- purefa_info - Certificate times changed to human readable rather than time since epoch
- purefa_info - new options added for information collection
- purefa_info - return dict names changed from ``ansible_facts`` to ``ra_info`` and ``user_info`` in approproate sections
- purefa_offload - Add support for Azure
- purefa_pgsnap - Add offload support
- purefa_snap - Allow recovery of deleted snapshot
- purefa_vg - Add QoS support

Bugfixes
--------

- purefa_host - resolve hostname case inconsistencies
- purefa_host - resolve issue found when using in Pure Storage Test Drive
