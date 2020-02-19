
purefa_pgsched -- Manage protection groups replication schedules on Pure Storage FlashArrays
============================================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Modify or delete protection groups replication schedules on Pure Storage FlashArrays.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 2.7
- purestorage



Parameters
----------

  blackout_start (optional, str, None)
    Specifies the time at which to suspend replication.

    Provide a time in 12-hour AM/PM format, eg. 11AM


  blackout_end (optional, str, None)
    Specifies the time at which to restart replication.

    Provide a time in 12-hour AM/PM format, eg. 5PM


  target_per_day (optional, int, None)
    Specifies the number of *per_day* replicated snapshots to keep beyond the *target_all_for* period.

    Maximum number is 1440


  schedule (True, str, None)
    Which schedule to change.


  per_day (optional, int, None)
    Specifies the number of *per_day* snapshots to keep beyond the *all_for* period.

    Maximum number is 1440


  snap_at (optional, int, None)
    Specifies the preferred time as HH:MM:SS, using 24-hour clock, at which to generate snapshots.

    Only valid if *snap_frequency* is an exact multiple of 86400, ie 1 day.


  api_token (True, str, None)
    FlashArray API token for admin privileged user.


  target_days (optional, int, None)
    Specifies the number of days to keep the *target_per_day* replicated snapshots beyond the *target_all_for* period before they are eradicated.

    Max retention period is 4000 days


  all_for (optional, int, None)
    Specifies the length of time, in seconds, to keep the snapshots on the source array before they are eradicated.

    Range available 1 - 34560000.


  fa_url (True, str, None)
    FlashArray management IPv4 address or Hostname.


  replicate_frequency (optional, int, None)
    Specifies the replication frequency in seconds.

    Range 14400 - 34560000.


  name (True, str, None)
    The name of the protection group.


  enabled (optional, bool, True)
    Enable the schedule being configured.


  days (optional, int, None)
    Specifies the number of days to keep the *per_day* snapshots beyond the *all_for* period before they are eradicated

    Max retention period is 4000 days


  state (optional, str, present)
    Define whether to set or delete the protection group schedule.


  replicate_at (optional, int, None)
    Specifies the preferred time as HH:MM:SS, using 24-hour clock, at which to generate snapshots.


  target_all_for (optional, int, None)
    Specifies the length of time, in seconds, to keep the replicated snapshots on the targets.

    Range is 1 - 34560000 seconds.


  snap_frequency (optional, int, None)
    Specifies the snapshot frequency in seconds.

    Range available 300 - 34560000.





Notes
-----

.. note::
   - This module requires the ``purestorage`` Python library
   - You must set ``PUREFA_URL`` and ``PUREFA_API`` environment variables if *fa_url* and *api_token* arguments are not passed to the module directly




Examples
--------

.. code-block:: yaml+jinja

    
    - name: Update protection group snapshot schedule
      purefa_pgsched:
        name: foo
        schedule: snapshot
        enabled: true
        snap_frequency: 86400
        snap_at: 15:30:00
        per_day: 5
        all_for: 5
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Update protection group replication schedule
      purefa_pgsched:
        name: foo
        schedule: replication
        enabled: true
        replicate_frequency: 86400
        replicate_at: 15:30:00
        target_per_day: 5
        target_all_for: 5
        blackout_start: 2AM
        blackout_end: 5AM
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Delete protection group snapshot schedule
      purefa_pgsched:
        name: foo
        scheduke: snapshot
        state: absent
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592
    
    - name: Delete protection group replication schedule
      purefa_pgsched:
        name: foo
        scheduke: replication
        state: absent
        fa_url: 10.10.10.2
        api_token: e31060a7-21fc-e277-6240-25983c6c4592




Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is maintained by community.



Authors
~~~~~~~

- Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>

