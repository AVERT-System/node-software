"""
Retrieve webcam images from Raspberry Pi camera using libcamera and picamera2.

:copyright:
    2024, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import numpy as np
try:
    from picamera2 import Picamera2 as pc2
    from libcamera import controls
except ModuleNotFoundError:
    class pc2:
        def __init__(self):
            pass
    print("Could not import Picamera2 module, some features may not work.")


def capture_image(
    camera: pc2 | None = None, camera_port: int | None = None
) -> np.ndarray:
    """
    Utility function that retrieves an image from the attached Raspberry Pi camera.
    
    """

    if camera is None:
        camera = pc2(camera_port)
        camera.set_controls(
            {
                "Saturation": 0.0,
                "AfMode": controls.AfModeEnum.Manual,
                "LensPosition": 0.0
            }
        )
        camera.start()

    return camera.capture_array()
