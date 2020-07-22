# python 3 headers, required if submitting to Ansible
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
        lookup: purefa_token
        author: Corey Wanless <corey.wanless@wwt.com>
        version_added: "2.9"
        short_description: Returns API token to utilized for further automation
        description:
            - This lookup takes in a username and password. It returns back an API token that can be used for automation against the array.
        options:
          _terms:
            description: Flash Array Hostname
            required: True
          fa_user:
            description: Login User
            required: True
          fa_password:
            description: Login Password
            required: True
          fa_api_version:
            description: Version of the FlashArray API. Defaults to 1.17
            required: False
"""
from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase

import requests


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):

        try:
            fa_url = terms[0]
        except:
            raise AnsibleError("Array URL not passed in")

        try:
            fa_user = kwargs['fa_user']
        except:
            raise AnsibleError("fa_user was not provided.")

        try:
            fa_password = kwargs['fa_password']
        except:
            raise AnsibleError("fa_password was not provided.")
        
        try:
            fa_api_version = kwargs['fa_api_version']
        except:
            fa_api_version = '1.17'

        try:
            fa_api_version = kwargs['fa_api_version']
        except:
            fa_api_version = '1.17'

        body = {
            "username": fa_user,
            "password": fa_password,
        }
        try:
            resp = requests.post('https://{}/api/{}/auth/apitoken'.format(fa_url, fa_api_version), verify=False, data=body)
            resp.raise_for_status()
        except:
            raise AnsibleError("Unable to access apitoken API")

        return [resp.json()['api_token']]
