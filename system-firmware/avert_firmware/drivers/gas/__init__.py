"""
This module contains a collection of drivers for a variety of gas measuring instruments.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

from datetime import datetime as dt

from avert_firmware.utilities import sync_data
from .vaisala import query_gmp343
from .novac import query as query_novac


def handle_query(instrument_config: dict, dirs: dict) -> None:
    """
    Handles queries to gas instruments attached to the AVERT system.

    Parameters
    ----------
    instrument_config: Gas instrument configuration information.
    dirs: Directories to use for receipt, archival, and transmission.

    """

    utc_now = dt.utcnow()

    print("Retrieving gas data file...")
    match instrument_config["model"]:
        case "vaisala-gmp343":
            filename = query_gmp343(utc_now, instrument_config, dirs)
        case "novac-doas":
            filename = query_novac(utc_now, instrument_config, dirs)

    print("Retrieval and sync of gas data complete.")
