"""
Migration functions for data files containing gas data.

:copyright:
    2024, the AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib


def _migrate_vaisala_co2_file(
    file_: pathlib.Path, archive_root: pathlib.Path, append_datatype: bool = False
) -> int:
    """
    Takes a new CO2 soil probe data file and shuttles it into an archive.

    - Receive file
    - Move file into archive
        - If the file with specific name already exists, append the data
        - If it doesn't, make it

    Parameters
    ----------
    file_: Path to the file in the upload directory.
    archive_root: Path to the root of the final archive.
    append_datatype: appends the data filetype to the root archive, if true.

    """

    if append_datatype:
        archive_root = archive_root / "soil-probe"

    archive_path_format = "{year}/{station}/{station}.{year}.{julday:03d}.CO2.csv"

    station, year, julday, *_ = file_.name.split(".")

    archive_file = archive_root / archive_path_format.format(
        year=year,
        station=station,
        julday=int(julday),
    )

    with file_.open("r") as f:
        data = f.readlines()

    if not archive_file.is_file():
        archive_file.parent.mkdir(exist_ok=True, parents=True)
        with archive_file.open("w") as f:
            print(data[0], file=f, end="")

    with archive_file.open("a") as f:
        print(data[1], file=f, end="")

    return 0
