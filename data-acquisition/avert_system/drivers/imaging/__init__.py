# -*- coding: utf-8 -*-
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
import pathlib
import subprocess
import sys
import time

import imageio.v3 as iio
import numpy as np

from avert_system.utilities import ping, read_config, sync_data
from avert_system.utilities.solar_tracker import is_it_daytime
from .netcam import capture_image as capture_image_netcam


def _write_image(
    dirs: dict, image_name: str, image: np.ndarray, quality: int = 75
) -> None:
    """Utility function that writes an image to file."""

    iio.imwrite(dirs["receive"] / image_name, image, quality=quality, optimize=True)


def handle_query(instrument: str, model: str) -> None:
    starttime = dt.utcnow()

    # --- Parse config files ---
    net_config = read_config("network")
    node_config = read_config("node")
    try:
        webcam_config = node_config.components.__getattribute__(instrument)
    except AttributeError:
        print(f"No '{instrument}' specified in the node configuration. Exiting.")
        sys.exit(1)

    data_dir = pathlib.Path(node_config.data_directory) / instrument
    site_code = f"{node_config.site_code}{node_config.site_code_extension}"
    component_ip = (
        f"{net_config.subnet}."
        f"{net_config.nodes.__getattribute__(site_code).__getattribute__(instrument)}"
    )

    # --- Make sure the network camera is available ---
    return_code = ping(component_ip)
    if return_code != 0:
        print("Camera not available. Exiting.")
        sys.exit(return_code)

    dirs = {
        "receive": data_dir / "receive",
        "transmit": data_dir / "transmit",
        "archive": data_dir / "ARCHIVE",
    }
    dirs["receive"].mkdir(exist_ok=True, parents=True)

    is_daytime = is_it_daytime(
        node_config.longitude,
        node_config.latitude,
        node_config.timezone,
        webcam_config.daylight_buffer,
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

        for i in range(webcam_config.frame_count):
            utcnow = dt.utcnow()

            image_name = (
                f"{utcnow.year}-{utcnow.month:02}-{utcnow.day:02d}_"
                f"{utcnow.hour:02d}{utcnow.minute:02d}{utcnow.second:02d}"
                ".jpg"
            )
            if i == 0 and webcam_config.mode == "video":
                video_name = f"{image_name.strip('.jpg')}.mp4"

            image = capture_image_netcam(component_ip)

            while transmit := True:
                # --- Image analysis code ---
                # Crop
                cropped_image = image[
                    webcam_config.min_y_pixel : webcam_config.max_y_pixel,
                    webcam_config.min_x_pixel : webcam_config.max_x_pixel,
                    :,
                ]
                _write_image(dirs, image_name, cropped_image, webcam_config.quality)

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

                if webcam_config.mode == "video":
                    transmit = False
                    break

            archive_path = f"{utcnow.year}-{utcnow.month:02}-{utcnow.day:02d}"
            sync_data(image_name, dirs, f"images/{archive_path}", transmit=transmit)

            time.sleep(webcam_config.time_between_frames)

            if not transmit and webcam_config.mode != "video":
                (dirs["receive"] / image_name).unlink()

        if webcam_config.mode == "video":
            cmd = (
                f"ffmpeg -framerate {webcam_config.frame_count} -pattern_type "
                f"glob -i '{dirs['receive'] / f'{archive_path}_*.jpg'}' -c:v "
                f"libx264 -pix_fmt yuv420p {dirs['receive'] / video_name}"
            )
            subprocess.run(cmd, shell=True)
            sync_data(video_name, dirs, f"videos/{archive_path}")

        for image_file in dirs["receive"].glob("*.jpg"):
            image_file.unlink()
