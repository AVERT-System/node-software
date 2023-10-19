# -*- coding: utf-8 -*-
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
import pathlib
import sys

from avert_system.utilities import (
    get_starttime_endtime,
    read_config,
    sync_data,
)
from .nanometrics import query_centaur


def handle_query(instrument: str, model: str) -> None:
    """
    Handles queries to seismic instruments attached to the AVERT system.

    Parameters
    ----------
    instrument: Instrument identifier e.g. 'seismic'.
    model: The model of instrument e.g. 'centaur'.

    """

    config = read_config()

    try:
        instrument_config = config["components"][instrument]
    except AttributeError:
        print(f"No '{instrument}' specified in the node configuration. Exiting.")
        sys.exit(1)

    starttime, endtime = get_starttime_endtime(
        dt.utcnow(),
        timestep=instrument_config["timestep"],
    )

    data_dir = pathlib.Path(config["data_archive"]) / instrument
    component_ip = (
        f"{config['network']['subnet']}."
        f"{config['components'][instrument]['ip_extension']}"
    )

    # --- Waveform data ---
    dirs = {
        "receive": data_dir / "receive",
        "transmit": data_dir / "transmit",
        "archive": data_dir / "ARCHIVE",
    }

    print("Retrieving waveform data...")
    for channel in instrument_config["channel_codes"]:
        print(f"  ...retrieving {channel} data...")

        match model:
            case "centaur":
                filename = query_centaur(
                    starttime,
                    endtime,
                    channel,
                    "D",
                    instrument_config,
                    component_ip,
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

    # --- SOH log data ---
    dirs = {
        "receive": data_dir / "SOH/receive",
        "transmit": data_dir / "SOH/transmit",
        "archive": data_dir / "ARCHIVE",
    }

    print("Retrieving SOH log data...")
    for channel in instrument_config["soh_channel_codes"]:
        print(f"  ...retrieving {channel} data...")

        match model:
            case "centaur":
                filename = query_centaur(
                    starttime,
                    endtime,
                    channel,
                    "S",
                    instrument_config,
                    component_ip,
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
