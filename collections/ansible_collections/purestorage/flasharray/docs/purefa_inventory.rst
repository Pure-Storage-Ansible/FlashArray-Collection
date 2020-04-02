
purefa_inventory -- Collect information from Pure Storage FlashArray
====================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Collect hardware inventory information from a Pure Storage Flasharray



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  fa_url (True, str, None)
    FlashArray management IPv4 address or Hostname.


  api_token (True, str, None)
    FlashArray API token for admin privileged user.





Notes
-----

.. note::
   - This module requires the ``purestorage`` Python library
   - You must set ``PUREFA_URL`` and ``PUREFA_API`` environment variables if *fa_url* and *api_token* arguments are not passed to the module directly




Examples
--------

.. code-block:: yaml+jinja

    
    - name: collect FlashArray invenroty
      purefa_inventory:
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    - name: show default information
      debug:
        msg: "{{ array_info['purefa_info'] }}"
    


Return Values
-------------

  purefa_inventory (always, complex, {'temps': {'CT0.TMP0': {'status': 'ok', 'temperature': 18}, 'CT0.TMP1': {'status': 'ok', 'temperature': 32}}, 'controllers': {'CT0': {'status': 'ok', 'model': None, 'serial': None}, 'CT1': {'status': 'ok', 'model': 'FA-405', 'serial': 'FHVBT52'}}, 'fans': {'CT0.FAN10': {'status': 'ok'}, 'CT0.FAN0': {'status': 'ok'}, 'CT0.FAN1': {'status': 'ok'}}, 'power': {'CT0.PWR0': {'status': 'ok', 'model': None, 'serial': None, 'voltage': None}, 'CT0.PWR1': {'status': 'ok', 'model': None, 'serial': None, 'voltage': None}}, 'interfaces': {'CT0.ETH0': {'status': 'ok', 'speed': 1000000000}, 'CT0.ETH1': {'status': 'ok', 'speed': 0}, 'CT1.IB1': {'status': 'ok', 'speed': 56000000000}, 'CT1.SAS0': {'status': 'ok', 'speed': 24000000000}, 'CT0.FC0': {'status': 'ok', 'speed': 8000000000}}, 'drives': {'SH0.BAY10': {'status': 'healthy', 'capacity': 511587647488, 'serial': 'S0WZNEACB00266', 'protocol': 'SAS', 'type': 'SSD'}, 'SH0.BAY1': {'status': 'healthy', 'capacity': 511587647488, 'serial': 'S0WZNEACC00517', 'protocol': 'SAS', 'type': 'SSD'}, 'SH0.BAY0': {'status': 'healthy', 'capacity': 2147483648, 'serial': 'S18NNEAFA01416', 'protocol': 'SAS', 'type': 'NVRAM'}}})
    Returns the inventory information for the FlashArray




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

