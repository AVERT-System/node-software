"""
This module contains a driver for communicating with and retrieving data from the 
Vaisala GMP343 CO2 probe.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

from datetime import datetime as dt
import sys

import numpy as np
import serial


def query(utc_now: dt, instrument_config: dict, dirs: dict) -> str:
    """
    Retrieve a burst of time-averaged CO2 measurements from the probe via the serial
    connection.

    Parameters
    ----------
    instrument_config: Seismometer configuration information.
    dirs: Directories to use for receipt, archival, and transmission.

    Returns
    -------
    filename: Name of the file containing the result of the request.

    """

    try:
        with serial.Serial(
            port=instrument_config["port"],
            baudrate=instrument_config["baudrate"],
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=3,
        ) as serial_connection:
            if not serial_connection.is_open:
                print(f"{serial_connection.name} is not open. Exiting.")
                serial_connection.close()
                sys.exit(1)

            print("Serial connection established, reading data...")
            co2_mean = np.mean(
                [
                    float(serial_connection.readline().strip())
                    for _ in range(instrument_config["sample_n"])
                ]
            )
            print("   ...success!")
    except serial.serialutil.SerialException:
        print(f"   ...could not open port {instrument_config['port']}. Exiting.")
        sys.exit(1)

    filename = instrument_config["file_format"].format(
        station=instrument_config["site_code"],
        datetime=utc_now,
        jday=utc_now.timetuple().tm_yday,
    )

    dirs["receive"].mkdir(exist_ok=True, parents=True)
    with (dirs["receive"] / filename).open("w") as f:
        print("datetime,co2", file=f)
        print(utc_now, co2_mean, file=f)

    return filename
