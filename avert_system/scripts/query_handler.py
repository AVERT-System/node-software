# -*- coding: utf-8 -*-
"""
This module provides the command-line interface entry points for data querying.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import argparse

from avert_system.instrument_drivers.cameras import handle_query as handle_query_camera
from avert_system.instrument_drivers.gnss_loggers import (
    handle_query as handle_query_gnss
)
from avert_system.instrument_drivers.magnetometers import (
    handle_query as handle_query_magnetic,
)
from avert_system.instrument_drivers.seismometers import (
    handle_query as handle_query_seismic,
)


fn_map = {
    "camera": handle_query_camera,
    "gnss": handle_query_gnss,
    "magnetic": handle_query_magnetic,
    "seismic": handle_query_seismic,
}


def query_handler(args=None):
    """
    A command-line entry point that handles parsing and dispatching of calls to query
    instruments attached to the node.

    """

    parser = argparse.ArgumentParser()

    sub_parser = parser.add_subparsers(
        title="instruments",
        dest="instrument",
        required=True,
        help="Specify the type of instrument to be queried.",
    )

    # --- Webcams ---
    query_camera = sub_parser.add_parser(
        "camera", help="Capture an image with a webcam."
    )
    query_camera.add_argument(
        "-m",
        "--model",
        help="Specify the model of camera to be queried.",
        choices=["netcam"],
        required=True,
    )

    # --- GNSS receivers ---
    query_gnss = sub_parser.add_parser("gnss", help="Query a GNSS receiver.")
    query_gnss.add_argument(
        "-m",
        "--model",
        help="Specify the model of GNSS receiver to be queried.",
        choices=["reftek"],
        required=True,
    )

    # --- Seismometers ---
    query_seismic = sub_parser.add_parser(
        "seismic", help="Query a seismometer/datalogger."
    )
    query_seismic.add_argument(
        "-m",
        "--model",
        help="Specify the model of seismometer/datalogger to be queried.",
        choices=["centaur"],
        required=True,
    )

    # --- Magnetometers ---
    query_magnetic = sub_parser.add_parser(
        "magnetic", help="Query a magnetometer/datalogger."
    )
    query_magnetic.add_argument(
        "-m",
        "--model",
        help="Specify the model of magnetometer/datalogger to be queried.",
        choices=["centaur"],
        required=True,
    )

    # --- Parse arguments and map to the corresponding instrument driver ---
    args = parser.parse_args()
    fn_map[args.instrument](**vars(args))
