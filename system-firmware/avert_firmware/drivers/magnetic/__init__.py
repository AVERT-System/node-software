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

from avert_firmware.utilities import (
    get_starttime_endtime,
    sync_data,
)
from .nanometrics import query_centaur


def handle_query(
    instrument_config: dict, component_ip: str, dirs: dict, model: str
) -> None:
    """
    Handles queries to magnetic instruments attached to the AVERT system.

    Parameters
    ----------
    instrument_config: Magnetometer configuration information.
    component_ip: Address of component within network.
    dirs: Directories to use for receipt, archival, and transmission.
    model: The model of instrument e.g. 'centaur'.

    """

    starttime, endtime = get_starttime_endtime(
        dt.utcnow(),
        timestep=instrument_config["timestep"],
    )

    print("Retrieving magnetic data...")
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
    print("Retrieval and sync of magnetic data complete.")
