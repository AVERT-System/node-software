# -*- coding: utf-8 -*-
"""
This module can be used to control the state of the switches on the network-attached
power relay.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import subprocess


def set_relay_state(
    ip: str,
    channel: str,
    state: int,
    username: str = "admin",
    password: str = "webrelay"
) -> None:
    """
    Change the state of a switch on a network-attached relay.

    Parameters
    ----------
    ip: The address of the network-attached relay.
    channel: The channel to change.
    state: The state to put the switch in.
    username: The admin username for the relay (optional).
    password: The admin password for the relay (optional).

    """

    command = [
        "curl",
        "-u",
        f"'{username}:{password}'",
        f"'http://{ip}/state.xml?relay{channel}State={state}'"
    ]
    print(command)

    return subprocess.run(command).returncode
