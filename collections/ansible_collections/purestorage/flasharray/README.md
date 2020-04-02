# Pure Storage FlashArray Collection

The Pure Storage FlashArray collection consists of the latest versions of the FlashArray modules and also includes support fro Cloud block Store
## Modules

- purefa_alert - manage email alert settings on the FlashArray
- purefa_arrayname - manage the name of the FlashArray
- purefa_banner - manage the CLI and GUI login banner of the FlashArray
- purefa_connect - manage FlashArrays connecting for replication purposes
- purefa_console - manage Console Lock setting for the FlashArray
- purefa_dns - manage the DNS settings of the FlashArray
- purefa_ds - manage the Directory Services of the FlashArray
- purefa_dsrole - manage the Directory Service Roles of the FlashArray
- purefa_endpoint - manage VMware protocol-endpoints on the FlashArray
- purefa_eula - sign, or resign, FlashArray EULA
- purefa_hg - manage hostgroups on the FlashArray
- purefa_host - manage hosts on the FlashArray
- purefa_info - get information regarding the configuration of the Flasharray
- purefa_network - manage the physical and virtual network settings on the FlashArray
- purefa_ntp - manage the NTP settings on the FlashArray
- purefa_offload - manage the offload targets for a FlashArray
- purefa_pg - manage protection groups on the FlashArray
- purefa_pgsched - manage protection group snapshot and replication schedules on the FlashArray
- purefa_pgsnap - manage protection group snapshots (local and remote) on the FlashArray
- purefa_phonehome - manage the phonehome setting for the FlashArray
- purefa_pod - manage ActiveCluster pods in FlashArrays
- purefa_proxy - manage the phonehome HTTPS proxy setting for the FlashArray
- purefa_ra - manage the Remote Assist setting for the FlashArray
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

## Requirements

- Ansible 2.9 or later
- Pure Storage FlashArray system running Purity 4.6 or later
- Pure Storage Cloud Block Store
- purestorage Python SDK
- netaddr

## Instructions

Install the Pure Storage FlashArray collection on your Ansible management host.

- Using ansible-galaxy (Ansible 2.9 or later):
```
ansible-galaxy collection install purestorage.flasharray -p ~/.ansible/collections
```

## Example Playbook
```yaml
- hosts: localhost
  gather_facts: true
  collections:
    - purestorage.flasharray
  tasks:
    - name: Get FlashArray information
      purefa_info:
        fa_url: 10.0.0.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592

    - name: Create a volume
      purefa_volume:
        name: foo
        size: 100G
        fa_url: 10.0.0.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592

    - name: Create a host
      purefa_host:
        name: "{{ ansible_hostname }}"
        protocol: iscsi
        iqn: "{{ ansible_iscsi_iqn }}"
        fa_url: 10.0.0.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
```

## License

[BSD-2-Clause](https://directory.fsf.org/wiki?title=License:FreeBSD)
[GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0.en.html)

## Author

This collection was created in 2019 by [Simon Dodsley](@sdodsley) for, and on behalf of, the [Pure Storage Ansible Team](pure-ansible-team@purestorage.com)
