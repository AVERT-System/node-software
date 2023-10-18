"""
This module provides utilities for telemetering data, both around a network (i.e. from
nodes to hubs) or to a remote server via an internet connection. 

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import argparse
import pathlib
import subprocess
import sys

from avert_system.drivers.network_relay import set_relay_state
from avert_system.utilities import ping, read_config, rsync


def _send_one_lan(file: pathlib.Path, ip: str, telemetry_config: dict) -> None:
    """
    Uses the rsync utility to send a file to a remote machine within the local area
    network.

    Parameters
    ----------
    file: The path to the file to be sent.
    ip: The address to which the file is to be sent.
    network_config: A dictionary containing telemetry information.

    """

    destination = (
        f"user@{ip}:{file.parents[1] / 'receive' / file.name}"
    )

    return rsync(file, destination, remove_source=True, max_attempts=1)


def _send_one_upload_server(
    file: pathlib.Path,
    ip: str,
    telemetry_config: dict
) -> None:
    """
    Uses the curl utility to send a file to a remote machine reachable via the internet.

    Parameters
    ----------
    file: The path to the file to be sent.
    ip: The address to which the file is to be sent.
    network_config: A dictionary containing telemetry information.

    """

    port = telemetry_config["target_port"]
    token = telemetry_config["token"]

    command = ["curl", f"-Ffile=@{file}", f"'http://{ip}:{port}/upload?token={token}'"]

    return subprocess.run(command).returncode


TELEMETRY_FN_LOOKUP = {
    "radio": _send_one_lan,
    "satellite": _send_one_upload_server,
}


def telemeter_data(args=None):
    """
    A command-line entry point that performs data telemetry either via radio-networked
    LAN or some form of internet connection to a remote server, whether that be by
    satellite or mobile data etc.

    By default, this command will send all files in the current transmit folders for
    each instrument stream attached.

    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-f",
        "--file",
        help="Specify a file to telemeter.",
        required=False,
    )

    parser.add_argument(
        "-d",
        "--destination",
        help="Specify a destination to which to telemeter the file.",
        required=False,
    )

    parser.add_argument(
        "-m",
        "--mode",
        help="Specify the mode of telemetry.",
        choices=["radio", "satellite"],
        required=False,
    )

    parser.add_argument(
        "-s",
        "--stream",
        help="Specify the filestream type to telemeter",
        choices=[
            "seismic",
            "magnetic",
            "geodetic",
            "weather",
            "site_health",
            "imagery",
            "ir_imagery",
            "doas",
        ],
        required=False,
    )

    parser.add_argument(
        "-l",
        "--file_limit",
        help="Specify a maximum number of files to send.",
        required=False,
    )

    args = parser.parse_args()

    config = read_config()

    # Determine telemetry method
    if mode := args.mode is None:
        mode = config["telemetry"]["telemeter_by"]

    # Check relevant telemetry equipment is present (satellite/radio transceiver)
    transceiver_ip = config["telemetry"]["transceiver_ip"]
    print(f"Searching for local telemetry equipment at {transceiver_ip}...")
    return_code = ping(transceiver_ip)
    if return_code != 0:
        print("   ...local telemetry equipment not found, attempting to power on...")
        return_code = set_relay_state(
            config["relay"]["ip"],
            config["relay"][mode],
            1,
        )
        if return_code != 0:
            print("   ...power on failed, exiting.")
            sys.exit(return_code)

        return_code = ping(transceiver_ip)
        if return_code != 0:
            print("   ...could not power local telemetry equipment, exiting.")
            sys.exit(return_code)
    print("...found.")

    # Check remote destination is visible
    if target_ip := args.destination is None:
        target_ip = config["telemetry"]["target_ip"]
    print(f"Searching for remote machine at {target_ip}...")
    return_code = ping(target_ip)
    if return_code != 0:
        print("   ...could not see remote machine, exiting.")
        sys.exit(return_code)

    if args.file is not None:
        TELEMETRY_FN_LOOKUP[mode](args.file, target_ip, config["telemetry"])
        sys.exit(0)

    data_dir = pathlib.Path("/home/user/data")

    if args.stream is not None:
        files = data_dir.glob(f"{args.stream}/transmit/*")
    else:
        files = data_dir.glob("*/transmit/*")

    if file_transfer_limit := args.file_limit is None:
        file_transfer_limit = 10_000

    for i, file in enumerate(files):
        if i == file_transfer_limit:
            sys.exit(0)
        TELEMETRY_FN_LOOKUP[mode](file, target_ip, config["telemetry"])
