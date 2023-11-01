"""
This module contains a collection of drivers for a variety of gas measuring instruments.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

from datetime import datetime as dt

from avert_system.utilities import sync_data
from .vaisala import query_gmp343
from .novac import query as query_novac


def handle_query(
    instrument_config: dict, component_ip: str, dirs: dict, model: str
) -> None:
    """
    Handles queries to gas instruments attached to the AVERT system.

    Parameters
    ----------
    instrument_config: Gas instrument configuration information.
    component_ip: Address of component within network.
    dirs: Directories to use for receipt, archival, and transmission.
    model: The model of instrument e.g. 'vaisala-gmp343'.

    """

    utc_now = dt.utcnow()

    print("Retrieving gas data file...")
    match model:
        case "vaisala-gmp343":
            filename = query_gmp343(utc_now, instrument_config, dirs)
        case "novac-doas":
            filename = query_novac(utc_now, component_ip, instrument_config, dirs)

    if filename is not None:
        print("   ...syncing data...")
        archive_path = instrument_config["archive_format"].format(
            station=instrument_config["site_code"],
            datetime=utc_now,
            jday=utc_now.timetuple().tm_yday,
        )
        sync_data(filename, dirs, archive_path)
    print("Retrieval and sync of gas data complete.")
