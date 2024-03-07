"""

:copyright:
    2024, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib

from .gas import _migrate_vaisala_co2_file
from .gnss import _migrate_sbf_file
from .images import _migrate_image_file
from .seismic import _migrate_miniseed_file


def id_file_format(file_: pathlib.Path):
    """
    Utility function used to automatically identify the data type/file format of a
    given file.

    Parameters
    ----------
    file_: Path to the file to be identified.

    Returns
    -------
    migration_fn: Callable function object that will handle the file migration.

    """

    if file_.suffix in [".jpg", ".png", ".jpeg"]:
        print("   ...image file identified...")
        return _migrate_image_file
    elif file_.suffix == ".sbf":
        print("   ...Septentrio binary format file identified...")
        return _migrate_sbf_file
    elif file_.suffix in [".m", ".mseed", ".msd"]:
        print("   ...miniSEED file identified...")
        return _migrate_miniseed_file
    elif "CO2.csv" in file_.name:
        print("   ...Vaisala CO2 soil probe file identified...")
        return _migrate_vaisala_co2_file
    else:
        print("   ...could not identify file.")
        return
