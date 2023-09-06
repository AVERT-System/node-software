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

from avert_system.drivers.imaging import handle_query as imaging_query
from avert_system.drivers.geodetic import handle_query as geodetic_query
from avert_system.drivers.magnetic import handle_query as magnetic_query
from avert_system.drivers.seismic import handle_query as seismic_query


fn_map = {
    "imaging": imaging_query,
    "geodetic": geodetic_query,
    "magnetic": magnetic_query,
    "seismic": seismic_query,
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
    imaging_parser = sub_parser.add_parser(
        "camera", help="Capture an image with a camera."
    )
    imaging_parser.add_argument(
        "-m",
        "--model",
        help="Specify the model of camera to be queried.",
        choices=["netcam"],
        required=True,
    )

    # --- GNSS receivers ---
    geodetic_parser = sub_parser.add_parser("geodetic", help="Query a GNSS receiver.")
    geodetic_parser.add_argument(
        "-m",
        "--model",
        help="Specify the model of GNSS receiver to be queried.",
        choices=["resolute_polar"],
        required=True,
    )

    # --- Seismometers ---
    seismic_parser = sub_parser.add_parser(
        "seismic", help="Query a seismometer/datalogger."
    )
    seismic_parser.add_argument(
        "-m",
        "--model",
        help="Specify the model of seismometer/datalogger to be queried.",
        choices=["centaur"],
        required=True,
    )

    # --- Magnetometers ---
    magnetic_parser = sub_parser.add_parser(
        "magnetic", help="Query a magnetometer/datalogger."
    )
    magnetic_parser.add_argument(
        "-m",
        "--model",
        help="Specify the model of magnetometer/datalogger to be queried.",
        choices=["centaur"],
        required=True,
    )

    # --- Parse arguments and map to the corresponding instrument driver ---
    args = parser.parse_args()
    fn_map[args.instrument](**vars(args))
