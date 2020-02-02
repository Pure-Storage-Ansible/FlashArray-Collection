
purefa_pod -- Manage AC pods in Pure Storage FlashArrays
========================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Manage AC pods in a Pure Storage FlashArray.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  state (optional, str, present)
    Define whether the pod should exist or not.


  target (optional, str, None)
    Name of clone target pod.


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  stretch (optional, str, None)
    The name of the array to stretch to/unstretch from. Must be synchromously replicated.

    To unstretch an array use state *absent*

    You can only specify a remote array, ie you cannot unstretch a pod from the current array and then restretch back to the current array.

    To restretch a pod you must perform this from the remaining array the pod resides on.


  failover (optional, list, None)
    The name of the array given priority to stay online if arrays loose contact with eachother.

    Oprions are either array in the cluster, or *auto*


  eradicate (optional, bool, False)
    Define whether to eradicate the pod on delete or leave in trash.


  fa_url (True, str, None)
    FlashArray management IPv4 address or Hostname.


  name (True, str, None)
    The name of the pod.





Notes
-----

.. note::
   - This module requires the ``purestorage`` Python library
   - You must set ``PUREFA_URL`` and ``PUREFA_API`` environment variables if *fa_url* and *api_token* arguments are not passed to the module directly




Examples
--------

.. code-block:: yaml+jinja

    
    - name: Create new pod named foo
      purefa_pod:
        name: foo
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: present
    
    - name: Delete and eradicate pod named foo
      purefa_pod:
        name: foo
        eradicate: yes
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: absent
    
    - name: Set failover array for pod named foo
      purefa_pod:
        name: foo
        failover:
        - array1
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Stretch a pod named foo to array2
      purefa_pod:
        name: foo
        stretch: array2
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Unstretch a pod named foo from array2
      purefa_pod:
        name: foo
        stretch: array2
        state: absent
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Create clone of pod foo named bar
      purefa_pod:
        name: foo
        target: bar
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
        state: present




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

