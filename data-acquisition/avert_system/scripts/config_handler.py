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
import json
import pathlib
import pprint
import shutil
import tomllib as toml

import yaml


config_dir = pathlib.Path.home() / ".config" / "avert" / "control"


def _init_config(args):
    """Create a simple example set of config files, useful for demo purposes."""

    print(f"Creating a basic config file and installing to {config_dir}.")
    config_dir.mkdir(parents=True, exist_ok=True)


def _install_config(args):
    """Install a config file to the AVERT system .config dir."""

    config_file = pathlib.Path(args.config).resolve()
    print(f"Attempting to install\n{config_file}\nto {config_dir}...")

    # Ensure file is a .toml/.json file that can be loaded
    if config_file.suffix not in [".toml", ".yml"]:
        print("...config files must have a valid file extension: '.toml' or '.yml'")
        return

    # Ensure file exists
    if not config_file.exists():
        print("...no such file.")
        return

    # Ensure the file is a valid TOML/JSON file
    with config_file.open("rb") as f:
        if config_file.suffix == ".toml":
            try:
                _ = toml.load(f)
            except toml.TOMLDecodeError:
                print("...file does not appear to be a valid TOML file.")
                return
        else:
            try:
                _ = yaml.safe_load(f)
            except json.JSONDecodeError:
                print("...file does not appear to be a valid JSON file.")
                return

    # First, make the relevant sub-directory (if not already present)
    target_dir = config_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    # And then copy the config
    shutil.copy(config_file, target_dir / f"{args.type}_config{config_file.suffix}")
    print("...success!")


def _uninstall_config(args):
    """Uninstall a config file from the AVERT system .config dir."""

    print(f"Attempting to uninstall\n{args.config}\nfrom {config_dir}...")
    config_file = pathlib.Path(args.config)
    if not config_file.is_file():
        print("...no such config file exists.")
        return
    config_file.unlink()
    print("...success!")


def _report_config(args):
    """Report the current AVERT system configuration."""

    config_file = config_dir / f"{args.type}_config.yml"

    # Ensure file is a .toml/.json file that can be loaded
    if config_file.suffix not in [".toml", ".yml"]:
        print("...config files must have a valid file extension: '.toml' or '.yml'")
        return

    # Ensure file exists
    if not config_file.exists():
        print("...system currently has no configuration file.")
        return

    # Ensure the file is a valid TOML/JSON file
    with config_file.open("rb") as f:
        if config_file.suffix == ".toml":
            try:
                config = toml.load(f)
            except toml.TOMLDecodeError:
                print("...file does not appear to be a valid TOML file.")
                return
        else:
            try:
                config = yaml.safe_load(f)
            except json.JSONDecodeError:
                print("...file does not appear to be a valid JSON file.")
                return

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(config)


fn_map = {
    "init": _init_config,
    "install": _install_config,
    "uninstall": _uninstall_config,
    "report": _report_config,
}


def config_handler(args=None):
    """
    Main entry point for the config command-line utility.

    """

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
        help="Name of the config.toml/.yml file to be uninstalled.",
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
    args = parser.parse_args(args)
    fn_map[args.command](args)
