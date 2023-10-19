# -*- coding: utf-8 -*-
"""
Module containing general utilities used throughout the package.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

from datetime import datetime as dt, timedelta as td
import pathlib
import subprocess
from subprocess import DEVNULL
import tomllib


def read_config() -> dict:
    """Utility function to read in configuration for the node/hub."""

    config_file = pathlib.Path.home() / ".config/avert/node_config.toml"
    with config_file.open("rb") as f:
        config = tomllib.load(f)

    return config


def sync_data(
    filename: str,
    dirs: dict,
    archive_path: str,
    new_filename: str = None,
    transmit: bool = True,
) -> None:
    """
    Sync data from the receive directory to the permanent archive and the
    transmit directory.

    Parameters
    ----------
    filename: Name of the file to be sync'd.
    dirs: Directories to use for receipt, archival, and transmission.
    archive_path: Describes any sub-directory structure in the archive.
    new_filename: Optionally, rename the file during the sync.
    transmit: Toggle for whether to also transmit file.

    """

    source_filename = destination_filename = filename
    if new_filename is not None:
        destination_filename = new_filename

    # Sync retrieved data to ARCHIVE
    archive_path = dirs["archive"] / archive_path
    pathlib.Path(archive_path).mkdir(exist_ok=True, parents=True)
    _ = rsync(
        source=str(dirs["receive"] / source_filename),
        destination=str(archive_path / destination_filename),
    )

    if transmit:
        # Sync retrieved data to transmit dir and remove from receive dir
        dirs["transmit"].mkdir(exist_ok=True, parents=True)
        _ = rsync(
            source=str(dirs["receive"] / source_filename),
            destination=str(dirs["transmit"] / destination_filename),
            remove_source=True,
        )


def ping(ip_address: str, max_attempts: int = 3) -> int:
    """
    Attempt to "ping" an IP address up to a maximum of 3 times.

    Parameters
    ----------
    ip_address: Address within network of device being pinged.

    Returns
    -------
    The return code - 0 = success, anything else = failure.

    """


    command = ["ping", "-c", "1", "-W", "3", ip_address]

    return _retry_command_on_failure(command, command[0], max_attempts)


def rsync(
    source: str, destination: str, remove_source: bool = False, max_attempts: int = 3
) -> int:
    """
    Utility function that attempts an rsync command a number of times.

    Parameters
    ----------
    source: Location of file to be sync'd.
    destination: Location to which file is to be sync'd.
    remove_source: Toggle for whether the source file is removed.
    max_attempts: Maximum number of attempts before deeming the sync a failure.

    Returns
    -------
    return_code: 0 = success, anything else = failure.

    """

    command = ["rsync", "-avq"]
    if remove_source:
        command.append("--remove-source-files")
    command.extend([source, destination])

    return _retry_command_on_failure(command, command[0], max_attempts)


def scp(source: str, destination: str, max_attempts: int = 3) -> int:
    """
    Utility function that attempts an scp command a number of times.

    Parameters
    ----------
    source: Location of file to be sync'd.
    destination: Location to which file is to be sync'd.
    max_attempts: Maximum number of attempts before deeming the sync a failure.

    Returns
    -------
    return_code: 0 = success, anything else = failure.

    """

    command = ["scp"]
    command.extend([source, destination])

    return _retry_command_on_failure(command, command[0], max_attempts)


def _retry_command_on_failure(command: list, command_name: str, max_attempts: int) -> int:
    """Re-run a command if it fails, up to a max number of attempts."""

    return_code, attempt = 1, 1
    while attempt <= max_attempts:
        try:
            return_code = subprocess.run(command, stdout=DEVNULL).returncode
            if return_code == 0:
                break
        except Exception as e:
            print(e)
            print(
                f"There was an issue with the {command_name} command - attempt"
                f" {attempt} of {max_attempts}."
            )
        attempt += 1

    return return_code


def get_starttime_endtime(now: dt, timestep: int = 10) -> tuple[dt, dt]:
    """
    Utility function to calculate the UTC start/end times to request.

    Parameters
    ----------
    now: Current time in UTC.
    timestep: Size of time span to request.

    Returns
    -------
    starttime, endtime: Beginning and end times of data window to request.

    """

    previous_timestep = now - td(minutes=timestep)
    start_minute = (previous_timestep.minute // timestep) * timestep
    starttime = dt(
        year=previous_timestep.year,
        month=previous_timestep.month,
        day=previous_timestep.day,
        hour=previous_timestep.hour,
        minute=start_minute,
    )
    endtime = starttime + td(minutes=timestep)

    return starttime, endtime
