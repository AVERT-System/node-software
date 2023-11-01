"""
This module contains a collection of drivers for a variety of commercial networked
webcameras.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

from datetime import datetime as dt
import subprocess
import time

import imageio.v3 as iio
import numpy as np

from avert_firmware.utilities import sync_data
from avert_firmware.utilities.solar_tracker import is_it_daytime
from .netcam import capture_image as capture_image_netcam


def _write_image(
    dirs: dict, image_name: str, image: np.ndarray, quality: int = 75
) -> None:
    """Utility function that writes an image to file."""

    iio.imwrite(dirs["receive"] / image_name, image, quality=quality, optimize=True)


def handle_query(
    instrument_config: dict, component_ip: str, dirs: dict, model: str, metadata: dict
) -> None:
    """
    Handles queries to cameras attached to the AVERT system.

    Parameters
    ----------
    instrument_config: Camera configuration information.
    component_ip: Address of component within network.
    dirs: Directories to use for receipt, archival, and transmission.
    model: The model of instrument e.g. 'stardot'.

    """

    starttime = dt.utcnow()

    is_daytime = is_it_daytime(
        metadata["longitude"],
        metadata["latitude"],
        metadata["timezone"],
        instrument_config["daylight_buffer"],
    )

    if is_daytime:
        # First image at the top of the hour is full resolution
        utcnow = dt.utcnow()
        if utcnow.minute <= 10:
            image_name = (
                f"{utcnow.year}-{utcnow.month:02}-{utcnow.day:02d}_"
                f"{utcnow.hour:02d}{utcnow.minute:02d}{utcnow.second:02d}"
                "_fullres.jpg"
            )

            image = capture_image_netcam(component_ip)
            _write_image(dirs, image_name, image)

            archive_path = f"{utcnow.year}-{utcnow.month:02}-{utcnow.day:02d}"
            sync_data(image_name, dirs, f"hires/{archive_path}")

            # Unlink image in receive dir now, saves faff later
            (dirs["receive"] / image_name).unlink()

        for i in range(instrument_config["frame_count"]):
            utcnow = dt.utcnow()

            image_name = (
                f"{utcnow.year}-{utcnow.month:02}-{utcnow.day:02d}_"
                f"{utcnow.hour:02d}{utcnow.minute:02d}{utcnow.second:02d}"
                ".jpg"
            )
            if i == 0 and instrument_config["mode"] == "video":
                video_name = f"{image_name.strip('.jpg')}.mp4"

            image = capture_image_netcam(component_ip)

            while transmit := True:
                # --- Image analysis code ---
                # Crop
                cropped_image = image[
                    instrument_config["min_y_pixel"] : instrument_config["max_y_pixel"],
                    instrument_config["min_x_pixel"] : instrument_config["max_x_pixel"],
                    :,
                ]
                _write_image(
                    dirs, image_name, cropped_image, instrument_config["quality"]
                )

                # Convert to greyscale
                greyscale = np.round(
                    np.dot(cropped_image, [0.2989, 0.5870, 0.1140])
                ).astype(np.uint8)

                # Assess average pixel brightness - this is an extra layer to
                # check if it is perhaps too dark to be useful
                brightness = np.mean(greyscale)

                if brightness < 80:
                    transmit = False
                    break

                # Assess "uniformity" of pixels - more uniform = more likely to
                # be cloudy, have water/snow on lens, etc
                uniformity = np.std(greyscale)

                if uniformity < 10000:
                    transmit = False
                    break

                if instrument_config["mode"] == "video":
                    transmit = False
                    break

            archive_path = f"{utcnow.year}-{utcnow.month:02}-{utcnow.day:02d}"
            sync_data(image_name, dirs, f"images/{archive_path}", transmit=transmit)

            time.sleep(instrument_config["time_between_frames"])

            if not transmit and instrument_config["mode"] != "video":
                (dirs["receive"] / image_name).unlink()

        if instrument_config["mode"] == "video":
            cmd = (
                f"ffmpeg -framerate {instrument_config['frame_count']} -pattern_type "
                f"glob -i '{dirs['receive'] / f'{archive_path}_*.jpg'}' -c:v "
                f"libx264 -pix_fmt yuv420p {dirs['receive'] / video_name}"
            )
            subprocess.run(cmd, shell=True)
            sync_data(video_name, dirs, f"videos/{archive_path}")

        for image_file in dirs["receive"].glob("*.jpg"):
            image_file.unlink()