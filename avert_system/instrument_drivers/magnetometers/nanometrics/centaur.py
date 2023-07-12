# -*- coding: utf-8 -*-
"""
This module contains drivers for the Nanometrics Centaur datalogger.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

from datetime import datetime as dt

import requests

from avert_system.utilities.errors import FileQueryException


def query(
    instrument: str,
    starttime: dt,
    endtime: dt,
    channel: str,
    stream_type: str,
    node_config: dict,
    component_ip: str,
    dirs: dict,
) -> str:
    """
    Construct the HTTP request to the Centaur datalogger onboard FDSNWS and save
    outputs to the "retrieve" folder.

    Parameters
    ----------
    instrument: Used to select the relevant configuration information from node_config.
    starttime: Beginning of time period of request.
    endtime: End of time period of request.
    channel: FDSN channel code descriptor.
    stream_type: SeisComp3 string to distinguish between data and logs.
    node_config: Seismometer configuration information.
    component_ip: Address of component within network.
    dirs: Directories to use for receipt, archival, and transmission.

    Returns
    -------
    filename: Name of the file containing the result of the request.

    Raises
    ------
    FileQueryException: If there is a failure to connect to the instrument.

    """

    # Construct the filename
    component_config = node_config.components.__getattribute__(instrument)
    location_code = component_config.location_code
    filename = component_config.file_format.format(
        network=node_config.network_code,
        station=node_config.site_code,
        location="" if location_code is None else location_code,
        channel=channel,
        stream_type=stream_type,
        datetime=starttime,
        jday=starttime.timetuple().tm_yday,
    )

    # Query Centaur for data matching request parameters
    url = (
        f"http://{component_ip}/fdsnws/dataselect/1/query?"
        f"network={node_config.network_code}&"
        f"station={node_config.site_code}&"
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
