#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2018, Simon Dodsley (simon@purestorage.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: purefa_token
version_added: '2.9'
short_description: Create of delete an API token for an existing admin user
description:
- Create or delete an API token for an existing admin user.
- Uses username/password to create/delete the API token.
author:
- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
options:
  state:
    description:
    - Create or delete API token
    type: str
    default: present
    choices: [ present, absent ]
  recreate:
    description:
    - Recreates the API token, overwriting the existing API token if present
    type: bool
    default: no
  username:
    description:
    - Username of the admin user to create API token for
    type: str
    required: true
  password:
    description:
    - Password of the admin user to create API token for.
    type: str
    required: true
  fa_url:
    description:
      - FlashArray management IPv4 address or Hostname.
    type: str
    required: true
'''

EXAMPLES = r'''
- name: Create API token
  purefa_arrayname:
    username: pureuser
    password: secret
    state: present
    fa_url: 10.10.10.2
- name: Delete API token
  purefa_arrayname:
    username: pureuser
    password: secret
    state: absent
    fa_url: 10.10.10.2
'''

RETURN = r'''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.flasharray.plugins.module_utils.purefa import get_system, purefa_argument_spec
from os import environ
import platform

VERSION = 1.0
USER_AGENT_BASE = 'Ansible_token'

HAS_PURESTORAGE = True
try:
    from purestorage import purestorage
except ImportError:
    HAS_PURESTORAGE = False


def get_session(module):
    """Return System Object or Fail"""
    user_agent = '%(base)s %(class)s/%(version)s (%(platform)s)' % {
        'base': USER_AGENT_BASE,
        'class': __name__,
        'version': VERSION,
        'platform': platform.platform()
    }

    array_name = module.params['fa_url']
    username = module.params['username']
    password = module.params['password']

    if HAS_PURESTORAGE:
        if array_name and username and password:
            system = purestorage.FlashArray(array_name, username=username, password=password, user_agent=user_agent)
        elif environ.get('PUREFA_URL'):
            if environ.get('PUREFA_USERNAME') and environ.get('PUREFA_PASSWORD'):
                url = environ.get('PUREFA_URL')
                username = environ.get('PUREFA_USERNAME')
                password = environ.get('PUREFA_PASSWORD')
                system = purestorage.FlashArray(url, username=username, password=password, user_agent=user_agent)
        else:
            module.fail_json(msg="You must set PUREFA_URL and PUREFA_USERNAME, PUREFA_PASSWORD "
                                 "environment variables or the fa_url, username and password "
                                 "module arguments")
        try:
            system.get()
        except Exception:
            module.fail_json(msg="Pure Storage FlashArray authentication failed. Check your credentials")
    else:
        module.fail_json(msg="purestorage SDK is not installed.")
    return system


def main():
    argument_spec = dict(
        fa_url=dict(),
        username=dict(type='str'),
        password=dict(no_log=True),
        state=dict(type='str', default='present', choices=['absent', 'present']),
        recreate=dict(type='bool'),
    )

    module = AnsibleModule(argument_spec, supports_check_mode=False)
    array = get_session(module)
    changed = False

    if module.params['username']:
        username = module.params['username']
    else:
        username = environ.get('PUREFA_USERNAME')
    state = module.params['state']
    recreate = module.params['recreate']

    result = array.get_api_token(admin=username)
    if state == 'present' and result['api_token'] is None:
        result = array.create_api_token(admin=username)
        changed = True
    elif state == 'present' and recreate:
        result = array.delete_api_token(admin=username)
        result = array.create_api_token(admin=username)
        changed = True
    elif state == 'absent' and result['api_token']:
        result = array.delete_api_token(admin=username)
        changed = True

    api_token = result['api_token']

    module.exit_json(changed=changed, purefa_token=api_token)


if __name__ == '__main__':
    main()
