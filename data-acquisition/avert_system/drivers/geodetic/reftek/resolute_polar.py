# -*- coding: utf-8 -*-
"""
This module contains drivers for the Resolute Polar GNSS receiver.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

from datetime import datetime as dt

import requests

from avert_system.utilities.errors import FileQueryException


def _encode_base36(number, alphabet="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    """Converts an integer to a base36 string."""

    base36 = ""

    if 0 <= number < len(alphabet):
        return alphabet[number]

    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36

    return base36


QUERY_FILENAME_FORMAT = (
    "{year}{jday:03d}/{serial_number}{filestream}{year_b36}{month}{day}{hour}.sbf"
)


def query(
    starttime: dt,
    filestream: str,
    instrument_config: dict,
    component_ip: str,
    dirs: dict,
) -> str:
    """
    Construct the HTTP request to the Resolute Polar GNSS receiver and save
    outputs to the "retrieve" folder.

    Parameters
    ----------
    starttime: Beginning of time period of request.
    endtime: End of time period of request.
    instrument_config: GNSS receiver configuration information.
    component_ip: Address of component within network.
    dirs: Directories to use for receipt, archival, and transmission.

    Returns
    -------
    filename: Name of the file containing the result of the request.

    Raises
    ------
    FileQueryException: If there is a failure to connect to the instrument.

    """

    # Construct the filename (for output)
    filename = instrument_config["file_format"].format(
        station=instrument_config["site_code"],
        datetime=starttime,
        jday=starttime.timetuple().tm_yday,
        rate=instrument_config["rate"],
        mtype=instrument_config["mtype"],
    )

    # Construct filename to query from logger
    query_filename = QUERY_FILENAME_FORMAT.format(
        year=starttime.strftime("%y"),
        jday=starttime.timetuple().tm_yday,
        serial_number=_encode_base36(instrument_config["serial_number"]).zfill(2),
        filestream=filestream,  # Filestream i.e. SD card 1
        year_b36=_encode_base36(int(starttime.strftime("%y"))).zfill(2),
        month=_encode_base36(starttime.month),
        day=_encode_base36(starttime.day),
        hour=_encode_base36(starttime.hour),
    )

    print(f"   ...attempting to download {query_filename}...")

    # Query Resolute Polar for data matching request parameters
    url = f"http://{component_ip}:{instrument_config['port']}/download/{query_filename}"

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
