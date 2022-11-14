# -*- coding: utf-8 -*-

# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright (c), Simon Dodsley <simon@purestorage.com>,2017
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

HAS_PURESTORAGE = True
try:
    from purestorage import purestorage
except ImportError:
    HAS_PURESTORAGE = False

HAS_PYPURECLIENT = True
try:
    from pypureclient import flasharray
except ImportError:
    HAS_PYPURECLIENT = False

HAS_REQUESTS = True
try:
    import requests
except ImportError:
    HAS_REQUESTS = False

from os import environ
import platform
import re

VERSION = 1.4
USER_AGENT_BASE = "Ansible"


def get_system(module):
    """Return System Object or Fail"""
    user_agent = "%(base)s %(class)s/%(version)s (%(platform)s)" % {
        "base": USER_AGENT_BASE,
        "class": __name__,
        "version": VERSION,
        "platform": platform.platform(),
    }
    array_name = module.params["fa_url"]
    api = module.params["api_token"]
    if HAS_PURESTORAGE:
        if array_name and api:
            system = purestorage.FlashArray(
                array_name, api_token=api, user_agent=user_agent
            )
        elif environ.get("PUREFA_URL") and environ.get("PUREFA_API"):
            system = purestorage.FlashArray(
                environ.get("PUREFA_URL"),
                api_token=(environ.get("PUREFA_API")),
                user_agent=user_agent,
            )
        else:
            module.fail_json(
                msg="You must set PUREFA_URL and PUREFA_API environment variables "
                "or the fa_url and api_token module arguments"
            )
        try:
            system.get()
        except Exception:
            module.fail_json(
                msg="Pure Storage FlashArray authentication failed. Check your credentials"
            )
    else:
        module.fail_json(msg="purestorage SDK is not installed.")
    return system


def get_array(module):
    """Return System Object or Fail"""
    user_agent = "%(base)s %(class)s/%(version)s (%(platform)s)" % {
        "base": USER_AGENT_BASE,
        "class": __name__,
        "version": VERSION,
        "platform": platform.platform(),
    }
    array_name = module.params["fa_url"]
    api = module.params["api_token"]
    if HAS_PYPURECLIENT and HAS_REQUESTS:
        versions = requests.get(
            "https://" + array_name + "/api/api_version", verify=False
        )
        valid_versions = [
            x for x in versions.json()["version"] if not re.search("[a-zA-Z]", x)
        ]
        api_version = valid_versions[-1]
        if array_name and api:
            system = flasharray.Client(
                target=array_name,
                api_token=api,
                user_agent=user_agent,
                version=api_version,
            )
        elif environ.get("PUREFA_URL") and environ.get("PUREFA_API"):
            system = flasharray.Client(
                target=(environ.get("PUREFA_URL")),
                api_token=(environ.get("PUREFA_API")),
                user_agent=user_agent,
            )
        else:
            module.fail_json(
                msg="You must set PUREFA_URL and PUREFA_API environment variables "
                "or the fa_url and api_token module arguments"
            )
        try:
            system.get_hardware()
        except Exception:
            module.fail_json(
                msg="Pure Storage FlashArray authentication failed. Check your credentials"
            )
    else:
        module.fail_json(msg="py-pure-client and/or requests are not installed.")
    return system


def purefa_argument_spec():
    """Return standard base dictionary used for the argument_spec argument in AnsibleModule"""

    return dict(
        fa_url=dict(),
        api_token=dict(no_log=True),
    )
