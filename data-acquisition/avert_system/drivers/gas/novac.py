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
import subprocess
import sys

from avert_system.utilities import scp, sync_data


def query(
    utc_now: dt, instrument_config: dict, component_ip: str, dirs: dict, model: str
) -> None:
    """
    Utility script that will pull data from the DOAS logger and sync with both a local
    redundant archive and the hub unit for telemetry.

    Parameters
    ----------
    instrument_config: Scanning DOAS configuration information.
    component_ip: Address of component within network.
    dirs: Directories to use for receipt, archival, and transmission.
    model: The model of instrument (not used, but would be 'novac' or similar).

    """

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
    archive_path = f"{utc_now.year}-{utc_now.month:02d}-{utc_now.day:02d}"
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
