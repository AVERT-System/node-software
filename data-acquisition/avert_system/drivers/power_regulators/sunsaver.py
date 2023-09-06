# -*- coding: utf-8 -*-
"""
This module contains drivers for the SunSaver solar controller series.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

from datetime import datetime as dt

import minimalmodbus as mmb
from serial import SerialException

from avert_system.utilities.errors import FileQueryException


REGISTERS = {
    "battery_voltage": (0x0008, 100/2**15),
    "array_voltage": (0x0009, 100/2**15),
    "load_voltage": (0x000A, 100/2**15),
    "charging_current": (0x000B, 79.16/2**15),
    "load_current": (0x000C, 79.16/2**15),
    "min_daily_voltage": (0x002B, 100/2**15),
    "max_daily_voltage": (0x002C, 100/2**15),
    "daily_charge": (0x002D, 0.1),
    "daily_load": (0x002E, 0.1),
    "ambient_temperature": (0x000F, 1.0),
    "charge_state": (0x0011, 1.0),
}


def query(
    tty: str,
    datetime: dt,
    dirs: dict,
) -> str:
    """
    Backend for the command-line script.

    Parameters
    ----------
    tty: Teletypewriter corresponding to the serial connection to the solar controller.
    datetime: The current time.
    dirs: Directories to use for receipt, archival, and transmission.

    Returns
    -------
    filename: Name of the file containing the result of the request.

    Raises
    ------
    FileQueryException: If there is a failure to connect to the solar controller.

    """

    filename = f"{datetime.date()}_{datetime.hour:02d}0000.csv"

    try:
        instrument = mmb.Instrument(f"/dev/{tty}", 10, mode="rtu")
        instrument.serial.baudrate = 9600
        instrument.serial.stopbits = 2

        register_values = [datetime.strftime("%Y-%m-%d %H:%M:%S")]
        for _, (addr, scale) in REGISTERS.items():
            register_values.append(
                instrument.read_register(registeraddress=addr, functioncode=2) * scale
            )
        print("    ...success!")
    except SerialException:
        print(f"Failed to open serial connection to teletypewriter at {tty}.")
        raise FileQueryException

    dirs["receive"].mkdir(exist_ok=True, parents=True)
    with (dirs["receive"] / filename).open("a") as f:
        if datetime.minute < 10:
            header = ["datetime"]
            header.extend(list(REGISTERS.keys()))
            print(",".join(header), file=f)
        print(",".join(register_values), file=f)

    return filename
