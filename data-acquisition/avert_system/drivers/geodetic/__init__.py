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
    model: The model of instrument e.g. 'resolute_polar'.

    """

    starttime, _ = get_starttime_endtime(dt.utcnow(), timestep=60)

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

    print("Retrieving GNSS data file...")
    match model:
        case "resolute_polar":
            filename = query_resolute_polar(
                starttime,
                "1",
                instrument_config,
                component_ip,
                dirs,
            )

    print("  ...syncing data...")
    archive_path = instrument_config["archive_format"].format(
        station=config["metadata"]["site_code"],
        datetime=starttime,
        jday=starttime.timetuple().tm_yday,
    )
    sync_data(filename, dirs, archive_path)
    print("Retrieval and sync of geodetic data complete.")
