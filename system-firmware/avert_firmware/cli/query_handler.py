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

from avert_firmware.drivers.imaging import handle_query as imagery_query
from avert_firmware.drivers.geodetic import handle_query as geodetic_query
from avert_firmware.drivers.gas import handle_query as gas_query
from avert_firmware.drivers.magnetic import handle_query as magnetic_query
from avert_firmware.drivers.seismic import handle_query as seismic_query
from avert_firmware.utilities import read_config


FN_MAP = {
    "imagery": imagery_query,
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

    parser.add_argument(
        "instrument",
        help="Specify the type of instrument to be queried.",
        choices=FN_MAP.keys(),
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

    kwargs["dirs"] = {
        "receive": data_dir / "receive",
        "transmit": data_dir / "transmit",
        "archive": data_dir / "ARCHIVE",
    }
    kwargs["dirs"]["receive"].mkdir(exist_ok=True, parents=True)

    match args.instrument:
        case "magnetic":
            pass
        case "seismic":
            pass
        case "gas":
            pass
        case "geodetic":
            pass
        case "imagery":
            kwargs["metadata"] = config["metadata"]

    # --- Map arguments to appropriate instrument driver ---
    FN_MAP[args.instrument](**kwargs)
