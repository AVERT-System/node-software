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

from avert_system.utilities import init_logging, read_config


def handle_query(instrument: str, model: str, debug: bool) -> None:
    starttime = dt.utcnow()

    # --- Spin up logging ---
    logger = init_logging(starttime, instrument, debug)

    # --- Parse config files ---
    net_config = read_config("network")
    node_config = read_config("node")
    try:
        weather_config = node_config.components.__getattribute__(instrument)
    except AttributeError:
        logger.info(f"No '{instrument}' specified in the node configuration. Exiting.")
        sys.exit(1)

    with serial.Serial(
        port=weather_config.port,
        baudrate=weather_config.baudrate,
        bytesize=8,
        parity="N",
        stopbits=1,
        timeout=3,
    ) as serial_connection:
        if not serial_connection.is_open:
            logger.info(f"{serial_connection.name} is not open. Exiting.")
            serial_connection.close()
            sys.exit(1)

        logger.info("Serial connection open, continuing.")
        while True:
            msg = serial_connection.readline()
            if len(msg) <= 0 or len(msg) > 200:
                logger.info("")
