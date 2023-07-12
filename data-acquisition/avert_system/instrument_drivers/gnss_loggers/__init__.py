# -*- coding: utf-8 -*-
"""
This module contains a collection of driver scripts for a variety of commercial
dataloggers for GNSS systems.

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
from .reftek import query_resolute_polar


def handle_query(instrument: str, model: str) -> None:
    """
    Handles queries to GNSS receivers attached to the AVERT system.

    Parameters
    ----------
    instrument: Instrument identifier e.g. 'geodetic'.
    model: The model of instrument (not used, but would be 'resolute_polar' or similar).

    """

    starttime, _ = get_starttime_endtime(dt.utcnow(), timestep=60)

    # --- Parse config files ---
    net_config = read_config("network")
    node_config = read_config("node")
    try:
        instrument_config = node_config.components.__getattribute__(instrument)
    except AttributeError:
        print(f"No '{instrument}' specified in the node configuration. Exiting.")
        sys.exit(1)

    data_dir = pathlib.Path(node_config.data_directory) / instrument
    site_code = f"{node_config.site_code}{node_config.site_code_extension}"
    component_ip = (
        f"{net_config.subnet}."
        f"{net_config.nodes.__getattribute__(site_code).__getattribute__(instrument)}"
    )

    dirs = {
        "receive": data_dir / "receive",
        "transmit": data_dir / "transmit",
        "archive": data_dir / "ARCHIVE",
    }

    print("Retrieving GNSS data file...")
    match model:
        case "resolute_polar":
            filename = query_resolute_polar(
                instrument,
                starttime,
                "1",
                node_config,
                component_ip,
                dirs,
            )

    print("  ...syncing data...")
    archive_path = instrument_config.archive_format.format(
        station=node_config.site_code,
        datetime=starttime,
        jday=starttime.timetuple().tm_yday,
    )
    sync_data(filename, dirs, archive_path)
    print("Retrieval and sync of geodetic data complete.")
