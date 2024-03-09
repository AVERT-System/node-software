"""
Migration functions for miniSEED data files.

:copyright:
    2024, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib
import subprocess


def _migrate_miniseed_file(
    file_: pathlib.Path, archive_root: pathlib.Path, append_datatype: bool = False
) -> int:
    """
    Takes a new miniseed file migrates it into the archive.

    If the data is from partway through a day, they are appended to an existing file,
    otherwise a new file is made.

    Parameters
    ----------
    file: Path to the file in the upload directory.
    archive: Path to the root of the final archive.
    append_datatype: appends the data filetype to the root archive, if true.

    """

    print("\t...miniseed file identified...")

    if append_datatype:
        archive_root = archive_root / "miniseed"

    archive_path_format = "{year}/{network}/{station}/{channel}.{data_type}"
    network, station, _, channel, _, year, *_ = file_.name.split(".")

    outfile = archive_root / archive_path_format.format(
        year=year,
        network=network,
        station=station,
        channel=channel,
        data_type="D",
    ) / file_.name

    outfile.parent.mkdir(parents=True, exist_ok=True)
    subprocess.Popen(["rsync", "-auz", file_, outfile]).wait()

    return 0
