"""
This module provides the command-line interface entry points for data querying.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import argparse
import pathlib
import sys

from avert_firmware.drivers.imaging import handle_query as imaging_query
from avert_firmware.drivers.geodetic import handle_query as geodetic_query
from avert_firmware.drivers.gas import handle_query as gas_query
from avert_firmware.drivers.magnetic import handle_query as magnetic_query
from avert_firmware.drivers.seismic import handle_query as seismic_query
from avert_firmware.utilities import ping, read_config


FN_MAP = {
    "imaging": imaging_query,
    "gas": gas_query,
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

    # --- Cameras ---
    imaging_parser = sub_parser.add_parser(
        "imaging", help="Capture an image with a camera."
    )
    imaging_parser.add_argument(
        "-m",
        "--model",
        help="Specify the model of camera to be queried.",
        choices=["netcam"],
        required=True,
    )

    # --- Gas monitors ---
    geodetic_parser = sub_parser.add_parser("gas", help="Query a gas monitoring instrument.")
    geodetic_parser.add_argument(
        "-m",
        "--model",
        help="Specify the model of gas monitoring instrument to be queried.",
        choices=["novac-doas", "vaisala-gmp343"],
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

    # --- Parse arguments ---
    args = parser.parse_args(sys.argv[2:])
    kwargs = {}

    config = read_config()

    try:
        kwargs["instrument_config"] = config["components"][args.instrument]
    except KeyError:
        print(f"No '{args.instrument}' specified in the node configuration. Exiting.")
        sys.exit(1)

    data_dir = pathlib.Path(config["data_archive"]) / args.instrument

    kwargs["component_ip"] = (
        f"{config['network']['subnet']}."
        f"{config['components'][args.instrument]['ip_extension']}"
    )

    kwargs["dirs"] = {
        "receive": data_dir / "receive",
        "transmit": data_dir / "transmit",
        "archive": data_dir / "ARCHIVE",
    }
    kwargs["dirs"]["receive"].mkdir(exist_ok=True, parents=True)

    kwargs["model"] = args.model

    match args.instrument:
        case "magnetic":
            pass
        case "seismic":
            pass
        case "gas":
            pass
        case "geodetic":
            pass
        case "imaging":
            kwargs["metadata"] = config["metadata"]

    print("Verifying instrument is visible on network...")
    return_code = ping(kwargs["component_ip"])
    if return_code != 0:
        print(f"Instrument not visible at: {kwargs['component_ip']}.\nExiting.")
        sys.exit(return_code)

    # --- Map arguments to appropriate instrument driver ---
    FN_MAP[args.instrument](**kwargs)
