"""
This module contains a collection of driver scripts for a variety of commercial
dataloggers for seismic systems.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

from datetime import datetime as dt

from avert_firmware.utilities import (
    get_starttime_endtime,
    sync_data,
)
from .nanometrics import query_centaur


def handle_query(instrument_config: dict, dirs: dict) -> None:
    """
    Handles queries to seismic instruments attached to the AVERT system.

    Parameters
    ----------
    instrument_config: Seismometer configuration information.
    dirs: Directories to use for receipt, archival, and transmission.

    """

    starttime, endtime = get_starttime_endtime(
        dt.utcnow(),
        timestep=instrument_config["timestep"],
    )

    print("Retrieving waveform data...")
    for channel in instrument_config["channel_codes"]:
        print(f"  ...retrieving {channel} data...")

        match instrument_config["model"]:
            case "centaur":
                filename = query_centaur(
                    starttime,
                    endtime,
                    channel,
                    "D",
                    instrument_config,
                    dirs,
                )

        print(f"  ...syncing {channel} data...")
        archive_path = instrument_config["archive_format"].format(
            network=instrument_config["network_code"],
            station=instrument_config["site_code"],
            channel=channel,
            stream_type="D",
            datetime=starttime,
        )
        sync_data(filename, dirs, archive_path)

    print("Retrieving SOH log data...")
    for channel in instrument_config["soh_channel_codes"]:
        print(f"  ...retrieving {channel} data...")

        match instrument_config["model"]:
            case "centaur":
                filename = query_centaur(
                    starttime,
                    endtime,
                    channel,
                    "S",
                    instrument_config,
                    dirs,
                )

        print(f"  ...syncing {channel} data...")
        archive_path = instrument_config["archive_format"].format(
            network=instrument_config["network_code"],
            station=instrument_config["site_code"],
            channel=channel,
            stream_type="S",
            datetime=starttime,
        )
        sync_data(filename, dirs, archive_path)
    print("Retrieval and sync of seismic data complete.")
