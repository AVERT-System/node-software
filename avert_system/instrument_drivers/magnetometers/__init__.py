# -*- coding: utf-8 -*-
"""
This module contains a collection of driver scripts for a variety of commercial
dataloggers for magnetic field systems.

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
    Handles queries to magnetic instruments attached to the AVERT system.

    Parameters
    ----------
    instrument: Instrument identifier e.g. 'magnetic'.
    model: The model of instrument (not used, but would be 'centaur' or similar).

    """

    # --- Parse config files ---
    net_config = read_config("network")
    node_config = read_config("node")
    try:
        instrument_config = node_config.components.__getattribute__(instrument)
    except AttributeError:
        print(f"No '{instrument}' specified in the node configuration. Exiting.")
        sys.exit(1)

    starttime, endtime = get_starttime_endtime(
        dt.utcnow(),
        timestep=instrument_config.timestep,
    )

    data_dir = pathlib.Path(node_config.data_directory) / instrument
    site_code = f"{node_config.site_code}{node_config.site_code_extension}"
    component_ip = (
        f"{net_config.subnet}."
        f"{net_config.nodes.__getattribute__(site_code).__getattribute__(instrument)}"
    )

    # --- Magnetic data ---
    dirs = {
        "receive": data_dir / "receive",
        "transmit": data_dir / "transmit",
        "archive": data_dir / "ARCHIVE",
    }

    print("Retrieving magnetic data...")
    for channel in instrument_config.channel_codes.split(","):
        print(f"  ...retrieving {channel} data...")

        match model:
            case "centaur":
                filename = query_centaur(
                    instrument,
                    starttime,
                    endtime,
                    channel,
                    "D",
                    node_config,
                    component_ip,
                    dirs,
                )

        print(f"  ...syncing {channel} data...")
        archive_path = instrument_config.archive_format.format(
            network=node_config.network_code,
            station=node_config.site_code,
            channel=channel,
            stream_type="D",
            datetime=starttime,
        )
        sync_data(filename, dirs, archive_path)
    print("Retrieval and sync of magnetic data complete.")
