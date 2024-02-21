"""
Retrieve webcam images from a networked webcam.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import sys

import imageio.v3 as iio
import numpy as np
import requests


def capture_image(ip: str) -> np.ndarray:
    """Utility function that retrieves an image via the camera's webserver."""
    try:
        r = requests.get(f"http://{ip}/image.jpg", stream=True)
    except OSError:
        print("Connection lost during capture. Exiting.")
        sys.exit(1)

    if r.status_code != 200:
        print("HTTP GET request failed - exiting.")
        sys.exit(r.status_code)

    return iio.imread(r.content)
