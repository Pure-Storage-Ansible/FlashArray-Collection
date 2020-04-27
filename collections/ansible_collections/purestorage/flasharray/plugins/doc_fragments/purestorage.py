# -*- coding: utf-8 -*-

# Copyright: (c) 2017, Simon Dodsley <simon@purestorage.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class ModuleDocFragment(object):

    # Standard Pure Storage documentation fragment
    DOCUMENTATION = r'''
options:
  - See separate platform section for more details
requirements:
  - See separate platform section for more details
notes:
  - Ansible modules are available for the following Pure Storage products: FlashArray, FlashBlade
'''

    # Documentation fragment for FlashArray
    FA = r'''
options:
  fa_url:
    description:
      - FlashArray management IPv4 address or Hostname.
    type: str
    required: true
  api_token:
    description:
      - FlashArray API token for admin privileged user.
    type: str
    required: true
notes:
  - This module requires the C(purestorage) Python library
  - You must set C(PUREFA_URL) and C(PUREFA_API) environment variables
    if I(fa_url) and I(api_token) arguments are not passed to the module directly
requirements:
  - python >= 2.7
  - purestorage >= 1.16
  - netaddr
'''
