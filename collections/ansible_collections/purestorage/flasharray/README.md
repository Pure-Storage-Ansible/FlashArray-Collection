# Pure Storage FlashArray Collection

The Pure Storage FlashArray collection consists of the latest versions of the FlashArray modules and also includes support for Cloud Block Store

## Supported Platforms

- Pure Storage FlashArray with Purity 4.6 or later
- Certain modules and functionality require higher versions of Purity. Modules will inform you if your Purity version is not high enough to use a module.

## Prerequisites

- Ansible 2.9 or later
- Pure Storage FlashArray system running Purity 4.6 or later
    - some modules require higher versions of Purity
- Some modules require specific Purity versions
- purestorage >=v1.19
- py-pure-client >=v1.8
- Python >=v2.7
- netaddr
- requests

## Idempotency

All modules are idempotent with the exception of modules that change or set passwords. Due to security requirements exisitng passwords can be validated against and therefore will always be modified, even if there is no change.

## Available Modules

- purefa_alert - manage email alert settings on the FlashArray
- purefa_arrayname - manage the name of the FlashArray
- purefa_banner - manage the CLI and GUI login banner of the FlashArray
- purefa_connect - manage FlashArrays connecting for replication purposes
- purefa_console - manage Console Lock setting for the FlashArray
- purefa_directory - manage FlashArray managed file system directories
- purefa_dns - manage the DNS settings of the FlashArray
- purefa_ds - manage the Directory Services of the FlashArray
- purefa_dsrole - manage the Directory Service Roles of the FlashArray
- purefa_endpoint - manage VMware protocol-endpoints on the FlashArray
- purefa_export - manage FlashArrray managed file system exports
- purefa_eula - sign, or resign, FlashArray EULA
- purefa_fs - manage FlashArray managed file systems
- purefa_hg - manage hostgroups on the FlashArray
- purefa_host - manage hosts on the FlashArray
- purefa_info - get information regarding the configuration of the Flasharray
- purefa_inventory - get hardware inventory information from a FlashArray
- purefa_network - manage the physical and virtual network settings on the FlashArray
- purefa_ntp - manage the NTP settings on the FlashArray
- purefa_offload - manage the offload targets for a FlashArray
- purefa_pg - manage protection groups on the FlashArray
- purefa_pgsched - manage protection group snapshot and replication schedules on the FlashArray
- purefa_pgsnap - manage protection group snapshots (local and remote) on the FlashArray
- purefa_phonehome - manage the phonehome setting for the FlashArray
- purefa_pod - manage ActiveCluster pods in FlashArrays
- purefa_pod_replica - manage ActiveDR pod replica links in FlashArrays
- purefa_policy - manage FlashArray NFS, SMB and snapshot policies
- purefa_proxy - manage the phonehome HTTPS proxy setting for the FlashArray
- purefa_ra - manage the Remote Assist setting for the FlashArray
- purefa_smis - manage SMI-S settings on the FlashArray
- purefa_smtp - manage SMTP settings on the FlashArray
- purefa_snap - manage local snapshots on the FlashArray
- purefa_snmp - manage SNMP settings on the FlashArray
- purefa_subnet - manage network subnets on the FlashArray
- purefa_syslog - manage the Syslog settings on the FlashArray
- purefa_timeout - manage the GUI idle timeout on the FlashArray
- purefa_user - manage local user accounts on the FlashArray
- purefa_vg - manage volume groups on the FlashArray
- purefa_vlan - manage VLAN interfaces on the FlashArray
- purefa_vnc - manage VNC for installed applications on the FlashArray
- purefa_volume - manage volumes on the FlashArray
- purefa_volume_tags - manage volume tags on the FlashArray

## Instructions

Install the Pure Storage FlashArray collection on your Ansible management host.

- Using ansible-galaxy (Ansible 2.9 or later):
```
ansible-galaxy collection install purestorage.flasharray -p ~/.ansible/collections
```

## License

[BSD-2-Clause](https://directory.fsf.org/wiki?title=License:FreeBSD)
[GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0.en.html)

## Author

This collection was created in 2019 by [Simon Dodsley](@sdodsley) for, and on behalf of, the [Pure Storage Ansible Team](pure-ansible-team@purestorage.com)
