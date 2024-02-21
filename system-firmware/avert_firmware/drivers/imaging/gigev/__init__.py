"""
This module contains a driver for capturing images using cameras that implement the
GigE-Vision interface standard.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import ctypes
import sys

from PIL import Image
import numpy as np

try:
    import avert_firmware.drivers.imaging.gigev.libgigev as gev
except OSError:
    print("Could not import GigE-V library")


def capture_image(instrument_config: dict) -> np.ndarray:
    """
    Captures an image using a camera that implements the GenICam/GigEV standard
    interface.

    Parameters
    ----------
    instrument_config: 

    Returns
    -------
    image: GigEV camera configuration information.

    """

    # Initialize the API
    gev.GevApiInitialize()

    # Allocate a maximum number of camera info structures.
    max_cameras = 16
    n_cameras = (ctypes.c_uint32)(0)
    camera_info = (gev.GEV_CAMERA_INFO * max_cameras)()

    status = gev.GevGetCameraList(camera_info, max_cameras, ctypes.byref(n_cameras))
    if status != 0:
        print(f"Error {status} getting camera list. Exiting.")
        sys.exit(status)

    if n_cameras.value == 0:
        print("No cameras found. Exiting.")
        sys.exit(1)

    handle = (ctypes.c_void_p)()
    status = gev.GevOpenCamera(camera_info[0], gev.GevExclusiveMode, ctypes.byref(handle))
    if status != 0:
        print(f"Error {status} opening camera. Exiting.")
        sys.exit(status)

    # Get the payload parameters
    print("   ...getting payload information...")
    payload_size = (ctypes.c_uint64)()
    pixel_format = (ctypes.c_uint32)()
    status = gev.GevGetPayloadParameters(
        handle, ctypes.byref(payload_size), ctypes.byref(pixel_format)
    )
    if status != 0:
        print(f"Error {status} getting camera payload parameters. Exiting.")
        _free_and_close_camera(handle)
        sys.exit(status)

    feature_strlen = (ctypes.c_int)(gev.MAX_GEVSTRING_LENGTH)
    unused = (ctypes.c_int)(0)

    width_str = ((ctypes.c_char) * feature_strlen.value)()
    height_str = ((ctypes.c_char) * feature_strlen.value)()
    status = gev.GevGetFeatureValueAsString(
        handle, b"Width", unused, feature_strlen, width_str
    )
    status = gev.GevGetFeatureValueAsString(
        handle, b"Height", ctypes.byref(unused), feature_strlen, height_str
    )

    buffer_address = ((ctypes.c_void_p) * instrument_config["buffers"])()
    for i in range(1):
        buffer_address[i] = ctypes.cast(
            ((ctypes.c_char) * payload_size.value)(), ctypes.c_void_p
        )

    status = gev.GevInitializeTransfer(
        handle, gev.Asynchronous, payload_size, instrument_config["buffers"], buffer_address
    )

    # Grab images to fill the buffer
    status = gev.GevStartTransfer(handle, instrument_config["buffers"])
    if status != 0:
        print(f"Error {status} starting transfer. Exiting.")
        _free_and_close_camera(handle)
        sys.exit(status)

    # Read the images out
    gev_buffer_ptr = ctypes.POINTER(gev.GEV_BUFFER_OBJECT)()

    tmout = (ctypes.c_uint32)(3000)
    status = gev.GevWaitForNextFrame(handle, ctypes.byref(gev_buffer_ptr), tmout.value)
    if status != 0:
        print(f"Error {status} waiting for frame. Exiting.")
        _free_and_close_camera(handle)
        sys.exit(status)

    gevbuf = gev_buffer_ptr.contents
    if gevbuf.status == 0:
        im_size = (gevbuf.w, gevbuf.h)
        im_addr = ctypes.cast(
            gevbuf.address,
            ctypes.POINTER(ctypes.c_ubyte * gevbuf.recv_size),
        )
        image = Image.frombuffer("L", im_size, im_addr.contents, "raw", "L", 0, 1)

    _free_and_close_camera(handle)

    return image


def _free_and_close_camera(handle):
    """Utility function to quickly free and close the camera."""

    gev.GevFreeTransfer(handle)
    gev.GevCloseCamera(ctypes.byref(handle))
    gev.GevApiUninitialize()
