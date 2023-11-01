"""
This module can be used to control the state of the switches on the network-attached
power relay.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import argparse
import subprocess
import sys

from avert_firmware.utilities import ping, read_config


def set_relay_state(
    ip: str,
    channel: str,
    state: int,
    username: str = "admin",
    password: str = "webrelay",
) -> int:
    """
    Change the state of a switch on a network-attached relay.

    Parameters
    ----------
    ip: The address of the network-attached relay.
    channel: The channel to change.
    state: The state to put the switch in.
    username: The admin username for the relay (optional).
    password: The admin password for the relay (optional).

    Returns
    -------
    return_code: Reports the outcome of the curl command.

    """

    return_code = ping(ip)
    if return_code != 0:
        print("   ...could not find network-attached relay switch.")
        return return_code

    command = [
        "curl",
        "-u",
        f"'{username}:{password}'",
        f"http://{ip}/state.xml?relay{channel}State={state}",
    ]

    return subprocess.run(command, stdout=subprocess.DEVNULL).returncode


def relay_cli(args=None):
    """
    A command-line entry point for controlling the network-attached relay switch.

    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--relay",
        help="Specify the switch to toggle.",
        choices=["1", "2", "3", "4"],
        required=True,
    )
    parser.add_argument(
        "-s",
        "--state",
        help="Specify the state to put the switch into.",
        choices=["open", "close"],
        required=True,
    )

    args = parser.parse_args(sys.argv[2:])

    config = read_config()

    return_code = ping(config["relay"]["ip"])
    if return_code != 0:
        print("   ...could not find network-attached relay switch.")
        return return_code

    state = 0 if args.state == "open" else 1

    _ = set_relay_state(config["relay"]["ip"], args.relay, state)
