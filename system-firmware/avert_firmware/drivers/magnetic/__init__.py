"""
This module contains a collection of driver scripts for a variety of commercial
dataloggers for magnetic field systems.

:copyright:
    2024, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

from datetime import datetime as dt

from avert_firmware.utilities import get_starttime_endtime
from avert_firmware.utilities.errors import FileQueryException
from .nanometrics import query_centaur


def handle_query(instrument_config: dict, dirs: dict) -> None:
    """
    Handles queries to magnetic instruments attached to the AVERT system.

    Parameters
    ----------
    instrument_config: Magnetometer configuration information.
    dirs: Directories to use for receipt, archival, and transmission.

    """

    starttime, endtime = get_starttime_endtime(
        dt.utcnow(),
        timestep=instrument_config["timestep"],
    )

    print("Retrieving magnetic data...")
    for channel in instrument_config["channel_codes"]:
        print(f"  ...retrieving {channel} data...")

        match instrument_config["model"]:
            case "centaur":
                try:
                    filename = query_centaur(
                        starttime,
                        endtime,
                        channel,
                        "D",
                        instrument_config,
                        dirs,
                    )
                except FileQueryException:
                    continue

    print("Retrieval and sync of magnetic data complete.")
