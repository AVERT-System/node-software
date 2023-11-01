"""
Utility for uploading configuration files to Resolute Polar dataloggers via serial
connection.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import argparse
import time

import serial
import yaml


def configure_resolute_polar():
    """
    A command-line script that configures a Xeos Technologies Resolute Polar GNSS
    receiver via serial connection.

    """

    parser = argparse.ArgumentParser()

    sub_parser = parser.add_subparsers(
        title="mode", dest="mode", required=True, help="Specify the mode."
    )

    # --- Upload ---
    config_upload = sub_parser.add_parser(
        "upload", help="Upload a new configuration from .toml file."
    )
    config_upload.add_argument(
        "-c",
        "--config",
        help="Path to configuration file to be uploaded.",
        required=True,
    )
    config_upload.add_argument(
        "-p",
        "--port",
        help="Device teletypewriter port. Default: '/dev/ttyACM0'.",
        required=False,
        default="/dev/ttyACM0",
    )

    # --- Validation ---
    config_validate = sub_parser.add_parser(
        "validate", help="Validate a configuration from .toml file."
    )
    config_validate.add_argument(
        "-c",
        "--config",
        help="Path to configuration file to be validated.",
        required=True,
    )
    config_validate.add_argument(
        "-p",
        "--port",
        help="Device teletypewriter port. Default: '/dev/ttyACM0'.",
        required=False,
        default="/dev/ttyACM0",
    )

    args = parser.parse_args()

    with open(args.config, "r") as stream:
        config = yaml.safe_load(stream)

    if args.mode == "upload":
        print("Uploading GNSS configuration...")
        with serial.Serial(args.port, 9600, timeout=0.1) as ser:
            # Run configure stages
            for system, items in config["config"].items():
                print(f"   ...{system}...")
                for key, value in items.items():
                    print(f"      ...{key}...")
                    command = f"\${key} {value}\r"
                    ser.write(command.encode())
                    time.sleep(0.5)

            # Reboot
            print("...complete - rebooting.")
            ser.write(b"\$resetnow\r")

    elif args.mode == "validate":
        with serial.Serial(args.port, 9600, timeout=0.1) as ser:
            while True:
                # Run validation checks
                validated = []
                print("Validating GNSS configuration...\n")
                for parameter, expect in config["checks"].items():
                    command = f"\${parameter}\r"
                    ser.write(command.encode())
                    response = ser.readline()

                    # Check against expected
                    if expect is None:
                        print(f"   {response.decode().split(' - ')[-1]}")
                    else:
                        print(f"   ...checking {parameter}...", end="")
                        if str(expect) not in response.decode():
                            print("invalid setting!")
                            print(f"      Expected:\n\t{expect}")
                            print(f"      Found:\n\t{response.decode()}")
                        print("\n")

                        validated.append(str(expect) in response.decode())
                break
            if all(validated):
                print("\nAll validation checks completed successfully.")
            else:
                print("Some settings did not check out.")
