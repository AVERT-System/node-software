"""
Migration functions for GNSS data files.

:copyright:
    2024, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

from datetime import datetime as dt
import pathlib
import subprocess

from avert_firmware.utilities import read_config


def _encode_base36(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    """Converts an integer to a base36 string."""

    base36 = ""

    if 0 <= number < len(alphabet):
        return alphabet[number]

    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36

    return base36


def _decode_base36(number):
    """Converts a base 36 string to an integer, base 10."""
    return int(number, 36)


def _migrate_sbf_file(
    file_: pathlib.Path, archive_root: pathlib.Path, append_datatype: bool = False
) -> int:
    """
    Takes a new GNSS data file and shuttles it into a field standard
    directory structure/file naming scheme.

    Files from the Resolute Polar have the following file name format:

    SSFYYMDH.sbf

    All characters are compressed into base 36
    S = Serial
    F = Stream source
    Y = 2-digit year
    M = Month
    D = Day
    H = Hour

    Parameters
    ----------
    file_: Path to the file in the upload directory.
    archive_root: Path to the root of the final archive.
    append_datatype: appends the data filetype to the root archive, if true.

    """

    config = read_config()
    site_lookup = config["gnss_site_lookup"]

    if append_datatype:
        archive_root = archive_root / "gnss"

    fname = file_.stem
    station = site_lookup[_decode_base36(fname[:2])]
    stream = fname[2]
    year = _decode_base36(fname[3:5])
    month = _decode_base36(fname[5])
    day = _decode_base36(fname[6])
    hour = _decode_base36(fname[7])

    datetime = dt.strptime(
        f"{year:02d}-{month:02d}-{day:02d} {hour:02d}", "%y-%m-%d %H"
    )
    jday = datetime.timetuple().tm_yday

    if stream == "1":
        # Standard data stream
        archive_path = archive_root / (
            f"raw/{datetime.year}/{jday:03d}/{station}"
        )
        outfile = archive_path / (
            f"{station}00US_R_{datetime.year}{jday:03d}{datetime.hour:02d}"
            f"00_01D_30S_MO.sbf"
        )
    elif stream == "2":
        # High-rate data stream
        archive_path = archive_root / (
            f"highrate/1-Hz/raw/{datetime.year}/{jday:03d}/{station}"
        )
        outfile = archive_path / (
            f"{station}00US_R_{datetime.year}{jday:03d}{datetime.hour:02d}"
            f"00_01H_01Z_MO.sbf"
        )
    elif stream == "3":
        # Navigation file
        archive_path = archive_root / f"raw/{datetime.year}/{jday:03d}/{station}"
        outfile = archive_path / (
            f"{station}00US_R_{datetime.year}{jday:03d}{datetime.hour:02d}"
            f"00_01D_MN.sbf"
        )
    elif stream == "4":
        # Receiver status file
        archive_path = archive_root / (
            f"status/raw/{datetime.year}/{jday:03d}/{station}"
        )
        outfile = archive_path / file_.name
    else:
        pass
    print(f"\t...file: {outfile.name}")
    outfile.parent.mkdir(parents=True, exist_ok=True)
    subprocess.Popen(["rsync", "-auz", file_, outfile]).wait()

    return 0
