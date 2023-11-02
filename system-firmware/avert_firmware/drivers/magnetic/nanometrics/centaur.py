"""
This module contains drivers for the Nanometrics Centaur datalogger.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

from datetime import datetime as dt
import sys

import requests

from avert_firmware.utilities import ping
from avert_firmware.utilities.errors import FileQueryException


def query(
    starttime: dt,
    endtime: dt,
    channel: str,
    stream_type: str,
    instrument_config: dict,
    dirs: dict,
) -> str:
    """
    Construct the HTTP request to the Centaur datalogger onboard FDSNWS and save
    outputs to the "retrieve" folder.

    Parameters
    ----------
    starttime: Beginning of time period of request.
    endtime: End of time period of request.
    channel: FDSN channel code descriptor.
    stream_type: SeisComp3 string to distinguish between data and logs.
    instrument_config: Seismometer configuration information.
    dirs: Directories to use for receipt, archival, and transmission.

    Returns
    -------
    filename: Name of the file containing the result of the request.

    Raises
    ------
    FileQueryException: If there is a failure to connect to the instrument.

    """

    # Construct the filename
    location_code = instrument_config["location_code"]
    filename = instrument_config["file_format"].format(
        network=instrument_config["network_code"],
        station=instrument_config["site_code"],
        location="" if location_code is None else location_code,
        channel=channel,
        stream_type=stream_type,
        datetime=starttime,
        jday=starttime.timetuple().tm_yday,
    )

    component_ip = instrument_config["ip"]
    print("   ...verifying instrument is visible on network...")
    return_code = ping(component_ip)
    if return_code != 0:
        print(f"Instrument not visible at: {component_ip}.\nExiting.")
        sys.exit(return_code)

    # Query Centaur for data matching request parameters
    url = (
        f"http://{component_ip}/fdsnws/dataselect/1/query?"
        f"network={instrument_config['network_code']}&"
        f"station={instrument_config['site_code']}&"
        f"location={'*' if location_code is None else location_code}&"
        f"channel={channel}&"
        f"starttime={str(starttime).replace(' ', 'T')}&"
        f"endtime={str(endtime).replace(' ', 'T')}"
    )

    r = requests.get(url)
    if r.status_code == 200:
        print("    ...success!")
    elif r.status_code == 204:
        print("    ...could not retrieve data, continuing...")
        raise FileQueryException

    dirs["receive"].mkdir(exist_ok=True, parents=True)
    with (dirs["receive"] / filename).open("wb") as f:
        f.write(r.content)

    return filename
