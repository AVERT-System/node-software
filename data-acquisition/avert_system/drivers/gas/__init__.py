# -*- coding: utf-8 -*-
"""
This module contains a driver for communicating with and retrieving data from the NOVAC
DOAS (Differential Optical Absorption Spectrometer) instrument.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

from datetime import datetime as dt
import pathlib
import subprocess
import sys

from avert_system.utilities import scp, ping, read_config, sync_data


def handle_query(instrument: str, model: str) -> None:
    """
    Utility script that will pull data from the DOAS logger and sync with both a local
    redundant archive and the hub unit for telemetry.

    Parameters
    ----------
    instrument: Instrument identifier e.g. 'doas'.
    model: The model of instrument (not used, but would be 'novac' or similar).

    """

    utcnow = dt.utcnow()

    config = read_config()

    try:
        instrument_config = config["components"][instrument]
    except AttributeError:
        print(f"No '{instrument}' specified in the node configuration. Exiting.")
        sys.exit(1)

    data_dir = pathlib.Path(config["data_archive"]) / instrument
    component_ip = (
        f"{config['network']['subnet']}."
        f"{config['components'][instrument]['ip_extension']}"
    )

    dirs = {
        "receive": data_dir / "receive",
        "transmit": data_dir / "transmit",
        "archive": data_dir / "ARCHIVE",
    }

    print("Verifying DOAS onboard computer is visible on network...")
    return_code = ping(component_ip)
    if return_code != 0:
        print(f"Onboard computer not visible at: {component_ip}.\nExiting.")
        sys.exit(return_code)

    print("Retrieving DOAS data...")
    dirs["receive"].mkdir(exist_ok=True, parents=True)
    return_code = scp(
        source=f"{instrument_config['username']}@{component_ip}:u0*.pak",
        destination=f"{dirs['receive']}/",
    )

    if return_code != 0:
        print("'scp' from DOAS computer failed. Exiting.")
        sys.exit(return_code)

    # --- Sync DOAS data, renaming ---
    archive_path = f"{utcnow.year}-{utcnow.month:02d}-{utcnow.day:02d}"
    today = dirs["archive"] / archive_path
    today.mkdir(exist_ok=True, parents=True)
    source_files = sorted(list(dirs["receive"].glob("*.pak")))
    for i, source_file in enumerate(source_files):
        # Only transmit every nth scan, specified in the config file.
        transmit = i % instrument_config["send_every"] == 0

        filecount = len(list(today.glob("*.pak")))
        filename = (
            f"{instrument_config['site_code']}_{archive_path}"
            f"_u{hex(filecount)[2:].zfill(3)}.pak"
        )

        print(f"   ...sync'ing {source_file.name} to {today / filename}...")
        sync_data(
            source_file.name,
            dirs,
            archive_path,
            new_filename=filename,
            transmit=transmit,
        )

    # Delete source files from onboard computer
    # Done in one go, rather than file by file, as the command-over-ssh is SLOW
    print("   ...removing source files from onboard computer...")
    return_code = subprocess.run(
        [
            *["ssh", f"{instrument_config['username']}@{component_ip}"],
            *["rm", "-f"],
            *[f"~/{source_file.name}" for source_file in source_files],
        ]
    ).returncode

    # Check if files have been shuttled to a sub-directory of ~/ on the NOVAC logger
    # This is done if the DOAS has rebooted, for example.
    remote_dirs, _ = subprocess.Popen(
        ["ssh", f"novac@{component_ip}", "ls", "-d", "r*/"], stdout=subprocess.PIPE
    ).communicate()
    if remote_dirs.decode() != "":
        for remote_dir in remote_dirs.decode().split():
            return_code = scp(
                source=(
                    f"{instrument_config['username']}"
                    f"@{component_ip}:{remote_dir}u*.pak"
                ),
                destination=f"{dirs['receive']}/",
            )

            if return_code != 0:
                print("'scp' failed. Exiting.")
                sys.exit(return_code)

            for source_file in dirs["receive"].glob("*.pak"):
                filecount = len(list(today.glob("*.pak")))
                filename = (
                    f"{instrument_config['site_code']}_{archive_path}"
                    f"_{hex(filecount)[2:].zfill(3)}.pak"
                )

                print(f"   ...sync'ing {source_file.name} to {today / filename}...")
                sync_data(source_file.name, dirs, archive_path, new_filename=filename)

        # Delete source directories from onboard computer
        # Done in one go, rather than file by file, as the command-over-ssh is SLOW
        print("   ...removing remote directories from onboard computer...")
        return_code = subprocess.run(
            [
                *["ssh", f"novac@{component_ip}", "rm", "-rf"],
                *[f"~/{remote_dir}" for remote_dir in remote_dirs.decode().split()],
            ]
        ).returncode

    print("Retrieval and sync of DOAS data complete.")
