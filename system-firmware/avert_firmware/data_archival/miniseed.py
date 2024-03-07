"""
Migration functions for miniSEED data files.

:copyright:
    2024, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib

import obspy


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

    try:
        st = obspy.read(str(file_))
    except TypeError:
        return 1

    if append_datatype:
        archive_root = archive_root / "miniseed"

    archive_path_format = "{year}/{network}/{station}/{channel}.{data_type}"
    filename_format = "{network}.{station}.{location}.{channel}.{data_type}.{year}.{jday:03d}"

    channels = list(set([tr.stats.channel for tr in st]))

    for channel in channels:
        channel_st = st.copy().select(channel=channel)

        starttime = min([tr.stats.starttime for tr in channel_st])

        archive_path = archive_root / archive_path_format.format(
            year=starttime.year,
            network=channel_st[0].stats.network,
            station=channel_st[0].stats.station,
            channel=channel_st[0].stats.channel,
            data_type="D",
        )
        archive_path.mkdir(parents=True, exist_ok=True)
        filename = filename_format.format(
            network=channel_st[0].stats.network,
            station=channel_st[0].stats.station,
            location=channel_st[0].stats.location,
            channel=channel_st[0].stats.channel,
            data_type="D",
            year=starttime.year,
            jday=starttime.julday,
        )
        print(f"\t...channel file: {filename}")
        if (archive_path / filename).is_file():
            print("\t    ...data from this day already exists -> appending...")
            merge_st = obspy.read(str(archive_path / filename))
            merge_st += channel_st
            merge_st.merge(method=-1)
            merge_st.write(str(archive_path / filename), format="MSEED")
        else:
            print("\t    ...no file for this day yet -> creating new file...")
            channel_st.write(str(archive_path / filename), format="MSEED")
    
    return 0
