"""
This module contains a collection of drivers for a variety of commercial networked
webcameras.

:copyright:
    2024, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

from datetime import datetime as dt
import sys
import time

import imageio.v3 as iio
import numpy as np
try:
    from picamera2 import Picamera2 as pc2
except ModuleNotFoundError:
    print("Could not import Picamera2 module, some features may not work.")

from avert_firmware.utilities.solar_tracker import is_it_daytime
from .stardot import capture_image as capture_image_stardot
from .gigev import capture_image as capture_image_gigev
from .picam import capture_image as capture_image_picam


def _write_image(
    image: np.ndarray, image_name: str, dirs: dict, quality: int = 75
) -> None:
    """Utility function that writes an image to file."""

    iio.imwrite(dirs["receive"] / image_name, image, quality=quality, optimize=True)


def handle_query(instrument_config: dict, dirs: dict, metadata: dict) -> None:
    """
    Handles queries to cameras attached to the AVERT system.

    Parameters
    ----------
    instrument_config: Camera configuration information.
    component_ip: Address of component within network.
    dirs: Directories to use for receipt, archival, and transmission.

    """

    print("Capturing images...")
    match instrument_config["model"]:
        case "gigev":
            for _ in range(instrument_config["frame_count"]):
                utcnow = dt.utcnow()
                julday = utcnow.timetuple().tm_yday
                image = capture_image_gigev(instrument_config)
                image_name = (
                    f"{metadata['vnum']}.{metadata['site_code']}."
                    f"{utcnow.year}.{julday:03d}_"
                    f"{utcnow.hour:02d}{utcnow.minute:02d}{utcnow.second:02d}-0000.jpg"
                )

                _write_image(image, image_name, dirs, instrument_config["quality"])

                time.sleep(instrument_config["time_between_frames"])
        case "stardot":
            daytime = is_it_daytime(
                metadata["longitude"],
                metadata["latitude"],
                metadata["timezone"],
                instrument_config["daylight_buffer"],
            )

            if not daytime:
                sys.exit(1)

            for _ in range(instrument_config["frame_count"]):
                utcnow = dt.utcnow()
                image = capture_image_stardot(instrument_config)
                image_name = (
                    f"{metadata['vnum']}.{metadata['site_code']}."
                    f"{utcnow.year}.{julday:03d}_"
                    f"{utcnow.hour:02d}{utcnow.minute:02d}{utcnow.second:02d}-0000.jpg"
                )

                _write_image(image, image_name, dirs, instrument_config["quality"])

                time.sleep(instrument_config["time_between_frames"])
        case "picam":
            daytime = is_it_daytime(
                metadata["longitude"],
                metadata["latitude"],
                metadata["timezone"],
                instrument_config["daylight_buffer"],
            )

            if not daytime:
                sys.exit(1)

            camera = pc2(instrument_config["camera_port"])
            for _ in range(instrument_config["frame_count"]):
                image = capture_image_picam(camera)
                utcnow = dt.utcnow()
                image_name = (
                    f"{metadata['vnum']}.{metadata['site_code']}."
                    f"{utcnow.year}.{julday:03d}_"
                    f"{utcnow.hour:02d}{utcnow.minute:02d}{utcnow.second:02d}-0000.jpg"
                )

                _write_image(image, image_name, dirs, instrument_config["quality"])

                time.sleep(instrument_config["time_between_frames"])
