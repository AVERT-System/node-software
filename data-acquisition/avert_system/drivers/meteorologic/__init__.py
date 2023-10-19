# -*- coding: utf-8 -*-
"""
This module contains a collection of driver scripts for a variety of commercial
meteorological (weather) stations.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

from datetime import datetime as dt
import sys

import serial


def handle_query(
    instrument_config: dict, component_ip: str, dirs: dict, model: str
) -> None:
    """
    Handles queries to meteorological instruments attached to the AVERT system.

    Parameters
    ----------
    instrument_config: Meteorological station configuration information.
    component_ip: Address of component within network.
    dirs: Directories to use for receipt, archival, and transmission.
    model: The model of instrument e.g. 'vaisala'.

    """

    starttime = dt.utcnow()

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

        print("Serial connection open, continuing.")
        while True:
            msg = serial_connection.readline()
            if len(msg) <= 0 or len(msg) > 200:
                print("")
