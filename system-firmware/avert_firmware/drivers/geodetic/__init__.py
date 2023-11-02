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

from avert_firmware.utilities import get_starttime_endtime, sync_data
from .reftek import query_resolute_polar


def handle_query(instrument_config: dict, dirs: dict) -> None:
    """
    Handles queries to GNSS receivers attached to the AVERT system.

    Parameters
    ----------
    instrument_config: GNSS receiver configuration information.
    dirs: Directories to use for receipt, archival, and transmission.

    """

    starttime, _ = get_starttime_endtime(dt.utcnow(), timestep=60)

    print("Retrieving GNSS data file...")
    match instrument_config["model"]:
        case "resolute_polar":
            filename = query_resolute_polar(
                starttime,
                "1",
                instrument_config,
                dirs,
            )

    print("  ...syncing data...")
    archive_path = instrument_config["archive_format"].format(
        station=instrument_config["site_code"],
        datetime=starttime,
        jday=starttime.timetuple().tm_yday,
    )
    sync_data(filename, dirs, archive_path)
    print("Retrieval and sync of geodetic data complete.")
