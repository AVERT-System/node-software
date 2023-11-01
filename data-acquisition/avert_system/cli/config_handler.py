# -*- coding: utf-8 -*-
"""
This module provides the command-line interface entry points that can be used to create,
install, remove, and report configuration files for the AVERT field system.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import argparse
import pathlib
import pprint
import shutil
import sys
import tomllib as toml


CONFIG_DIR = pathlib.Path.home() / ".config" / "avert" / "control"


def _install_config(args):
    """Install a config file to the AVERT system .config dir."""

    config_file = pathlib.Path(args.config).resolve()
    print(f"Attempting to install\n{config_file}\nto {CONFIG_DIR}...")

    # Ensure file is a .toml file that can be loaded
    if config_file.suffix != ".toml":
        print("...config files must use the TOML file format.")
        sys.exit(1)

    # Ensure file exists
    if not config_file.exists():
        print("...no such file.")
        sys.exit(1)

    # Ensure the file is a valid TOML/JSON file
    with config_file.open("rb") as f:
        try:
            _ = toml.load(f)
        except toml.TOMLDecodeError:
            print("...file does not appear to be a valid TOML file.")
            sys.exit(1)

    # First, make the relevant sub-directory (if not already present)
    target_dir = CONFIG_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    # And then copy the config
    shutil.copy(config_file, target_dir / f"{args.type}_config{config_file.suffix}")
    print("...success!")


def _uninstall_config():
    """Uninstall a config file from the AVERT system .config dir."""

    config_file = CONFIG_DIR / "node_config.toml"

    print("Attempting to uninstall config file...")

    # Ensure file exists
    if not config_file.exists():
        print(f"...no such configuration file at {config_file}.")
        sys.exit(1)

    config_file.unlink()
    print("...success!")


def _report_config():
    """Report the current AVERT system configuration."""

    config_file = CONFIG_DIR / "node_config.toml"

    # Ensure file exists
    if not config_file.exists():
        print(f"...no such configuration file at {config_file}.")
        sys.exit(1)

    # Ensure the file is a valid TOML/JSON file
    with config_file.open("rb") as f:
        try:
            config = toml.load(f)
        except toml.TOMLDecodeError:
            print("...file does not appear to be a valid TOML file.")
            sys.exit(1)

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(config)


FN_MAP = {
    "install": _install_config,
    "uninstall": _uninstall_config,
    "report": _report_config,
}


def config_handler(args=None):
    """Main entry point for the config command-line utility."""

    parser = argparse.ArgumentParser()
    sub_parser = parser.add_subparsers(
        title="commands",
        dest="command",
        required=True,
        help="Specify the mode to run in.",
    )

    # Init command
    _ = sub_parser.add_parser("init", help="Initialise a basic config file.")

    # Install command
    install_conf = sub_parser.add_parser("install", help="Install a new config file.")
    install_conf.add_argument(
        "-c",
        "--config",
        help="Path to the config.toml/.yml file to be installed.",
        required=True,
    )
    install_conf.add_argument(
        "-t",
        "--type",
        help="Specify the type of config file to install.",
        choices=["network", "node"],
        required=True,
    )

    # Uninstall command
    uninstall_conf = sub_parser.add_parser(
        "uninstall", help="Uninstall an existing config file."
    )
    uninstall_conf.add_argument(
        "-c",
        "--config",
        help="Name of the .toml file to be uninstalled.",
        required=True,
    )

    # Report command
    report_conf = sub_parser.add_parser(
        "report", help="Report the current configuration."
    )
    report_conf.add_argument(
        "-t",
        "--type",
        help="Specify the type of configuration to report.",
        choices=["network", "node"],
        required=True,
    )

    # Parse arguments and execute relevant function
    args = parser.parse_args(sys.argv[2:])
    FN_MAP[args.command](args)
