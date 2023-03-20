#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2021, Simon Dodsley (simon@purestorage.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: purefa_syslog_settings
version_added: '1.10.0'
short_description: Manage FlashArray syslog servers settings
description:
- Manage FlashArray syslog servers settings
author:
- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
options:
  severity:
    description:
    - Logging severity threshold for which events will be forwarded to the
      configured syslog servers.
    default: info
    choices: [ debug, info, notice ]
    type: str
  ca_certificate:
    type: str
    description:
    - The text of the CA certificate for condifured syslog servers.
    - Includes the "-----BEGIN CERTIFICATE-----" and "-----END CERTIFICATE-----" lines
    - Does not exceed 3000 characters in length
    - To delete the existing CA certifcate use the special string `DELETE`
  tls_audit:
    type: bool
    default: true
    description:
    - If messages that are necessary in order to audit TLS negotiations
      performed by the array are forwared to the syslog servers.
extends_documentation_fragment:
- purestorage.flasharray.purestorage.fa
"""

EXAMPLES = r"""
- name: Change syslog servers settings
  purestorage.flasharray.purefa_syslog_servers:
    tls_audit: false
    severity: debug
    ca_certificate: "{{lookup('file', 'example.crt') }}"
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

- name: Delete existing CA certifcate for syslog servers settings
  purestorage.flasharray.purefa_syslog_servers:
    ca_certificate: DELETE
    fa_url: 10.10.10.2
    api_token: e31060a7-21fc-e277-6240-25983c6c4592

"""

RETURN = r"""
"""

HAS_PURESTORAGE = True
try:
    from pypureclient import flasharray
except ImportError:
    HAS_PURESTORAGE = False

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.flasharray.plugins.module_utils.purefa import (
    get_system,
    get_array,
    purefa_argument_spec,
)

MIN_REQUIRED_API_VERSION = "2.9"


def main():
    argument_spec = purefa_argument_spec()
    argument_spec.update(
        dict(
            severity=dict(
                type="str",
                default="info",
                choices=["info", "debug", "notice"],
            ),
            tls_audit=dict(type="bool", default=True),
            ca_certificate=dict(type="str", no_log=True),
        )
    )

    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
    )

    if not HAS_PURESTORAGE:
        module.fail_json(msg="py-pure-client sdk is required for this module")

    array = get_system(module)
    api_version = array._list_available_rest_versions()

    if MIN_REQUIRED_API_VERSION not in api_version:
        module.fail_json(
            msg="Purity//FA version not supported. Minimum version required: 6.2.0"
        )

    array = get_array(module)
    changed = cert_change = False
    if module.params["ca_certificate"] and len(module.params["ca_certificate"]) > 3000:
        module.fail_json(msg="Certificate exceeds 3000 characters")
    current = list(array.get_syslog_servers_settings().items)[0]
    try:
        if current.ca_certificate:
            pass
    except AttributeError:
        current.ca_certificate = None
    if current.tls_audit_enabled != module.params["tls_audit"]:
        changed = True
        new_tls = module.params["tls_audit"]
    else:
        new_tls = current.tls_audit_enabled
    if current.logging_severity != module.params["severity"]:
        changed = True
        new_sev = module.params["severity"]
    else:
        new_sev = current.logging_severity
    if module.params["ca_certificate"]:
        if module.params["ca_certificate"].upper() == "DELETE":
            if current.ca_certificate:
                cert_change = changed = True
                new_cert = ""
        elif current.ca_certificate != module.params["ca_certificate"]:
            cert_change = changed = True
            new_cert = module.params["ca_certificate"]
    if changed and not module.check_mode:
        if cert_change:
            res = array.patch_syslog_servers_settings(
                syslog_server_settings=flasharray.SyslogServerSettings(
                    ca_certificate=new_cert,
                    tls_audit_enabled=new_tls,
                    logging_severity=new_sev,
                )
            )
        else:
            res = array.patch_syslog_servers_settings(
                syslog_server_settings=flasharray.SyslogServerSettings(
                    tls_audit_enabled=new_tls, logging_severity=new_sev
                )
            )
        if res.status_code != 200:
            module.fail_json(
                msg="Changing syslog settings failed. Error: {0}".format(
                    res.errors[0].message
                )
            )

    module.exit_json(changed=changed)


if __name__ == "__main__":
    main()
