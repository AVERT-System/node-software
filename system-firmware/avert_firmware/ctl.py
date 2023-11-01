"""
This module acts as a dispatcher for the top level command options for the `avertctl`
command-line utility.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import argparse
import sys

from avert_firmware.cli import config_handler, query_handler, telemeter_data
from avert_firmware.drivers.network_relay import relay_cli


FN_MAP = {
    "configure": config_handler,
    "data-query": query_handler,
    "telemeter": telemeter_data,
    "toggle-relay": relay_cli,
}


def cli(args=None):
    """
    A command-line interface for the AVERT system, providing a single entry point for
    configuring and interacting with the AVERT system software.

    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "command",
        help="top-level command used to select a sub-utility.",
        choices=FN_MAP.keys(),
    )

    args = parser.parse_args(sys.argv[1:2])

    FN_MAP[args.command]()
