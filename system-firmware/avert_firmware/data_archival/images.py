"""
Migration functions for imagery files.

:copyright:
    2024, the AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

from datetime import datetime as dt
import pathlib
import sqlite3
import subprocess


def _migrate_image_file(
    file_: pathlib.Path, archive_root: pathlib.Path, append_datatype: bool = False
):
    """
    Identify the type of image and migrate into the relevant archive.

    Parameters
    ----------
    file: Path to the file in the upload directory.
    archive: Path to the root of the final archive.
    append_datatype: appends the data filetype to the root archive, if true.

    """

    image_type = file_.parents[1].name

    match image_type:
        case "infrared":
            return _migrate_infrared_image(file_, archive_root, append_datatype)
        case "visible":
            return _migrate_visible_image(file_, archive_root, append_datatype)


def _create_connection(db_file: str) -> None:
    """
    Create a new database connection to the SQLite database specified by the
    db_file.

    """

    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(f"Error: {e}.")

    return conn


def _add_image2db(image: pathlib.Path, image_type: str):
    """
    Add a new image to a database.

    Parameters
    ----------
    image: Path to the image file to be added to the database.
    image_type: Descriptor specifying the type of image (e.g., infrared, visible, etc).

    """

    conn = _create_connection("/home/webmaster/data-api/data/imagery.db")
    with conn:
        cursor = conn.cursor()
        vnum, station, year, julday_timeframe, ext = image.name.split(".")
        julday, timeframe = julday_timeframe.split("_")
        time, frame = timeframe.split("-")

        timestamp = dt.strptime(f"{year}-{julday}_{time}", "%Y-%j_%H%M%S")

        new_image = {
            "image_id": str(image.stem),
            "url": str(image),
            "vnum": vnum,
            "site": str(station),
            "frame": int(frame),
            "file_format": ext,
            "quality": 0,
            "timestamp": timestamp,
        }
        try:
            print(f"Adding {image.stem} to database...")
            if image_type == "visible":
                cursor.execute(
                    """
                    INSERT INTO visible(image_id,url,vnum,site,frame,file_format,quality,timestamp)
                    VALUES(?,?,?,?,?,?,?,?)
                    """,
                    tuple(new_image.values()),
                )
            elif image_type == "infrared":
                cursor.execute(
                    """
                    INSERT INTO infrared(image_id,url,vnum,site,frame,file_format,quality,timestamp)
                    VALUES(?,?,?,?,?,?,?,?)
                    """,
                    tuple(new_image.values()),
                )
        except sqlite3.IntegrityError as e:
            if "UNIQUE" in str(e):
                print("Image already in database.")
        conn.commit()
        cursor.close()


def _migrate_infrared_image(
    file_: pathlib.Path, archive_root: pathlib.Path, append_datatype: bool = False
) -> int:
    """
    Takes new infrared spectrum images and migrates them into the archive.

    Parameters
    ----------
    file: Path to the file in the upload directory.
    archive: Path to the root of the final archive.
    append_datatype: appends the data filetype to the root archive, if true.

    """

    print("\t...infrared image file identified...")

    if append_datatype:
        archive_root = archive_root / "imagery"

    archive_structure = "{vnum}/{year}/{station}/still/{julday:03d}"

    vnum, station, year, julday = file_.name.split("_")[0].split(".")
    archive_path = archive_root / "infrared" / archive_structure.format(
        vnum=vnum,
        year=year,
        station=station,
        julday=int(julday),
    )
    archive_path.mkdir(parents=True, exist_ok=True)

    new_file_path = archive_path / file_.name
    subprocess.Popen(["rsync", "-auz", file_, new_file_path]).wait()

    if append_datatype:
        # On server
        print("\t    ...adding to database...")
        _add_image2db(new_file_path, "infrared")

    return 0


def _migrate_visible_image(
    file_: pathlib.Path, archive_root: pathlib.Path, append_datatype: bool = False
) -> int:
    """
    Takes new visible spectrum images and migrates them into the archive.

    Parameters
    ----------
    file: Path to the file in the upload directory.
    archive: Path to the root of the final archive.
    append_datatype: appends the data filetype to the root archive, if true.

    """

    print("\t...visible image file identified...")

    if append_datatype:
        archive_root = archive_root / "imagery"

    archive_structure = "{vnum}/{year}/{station}/still/{julday:03d}"

    vnum, station, year, julday = file_.name.split("_")[0].split(".")
    archive_path = archive_root / "visible" / archive_structure.format(
        vnum=vnum,
        year=year,
        station=station,
        julday=int(julday),
    )
    archive_path.mkdir(parents=True, exist_ok=True)

    new_file_path = archive_path / file_.name
    subprocess.Popen(["rsync", "-auz", file_, new_file_path]).wait()

    if append_datatype:
        # On server
        print("\t    ...adding to database...")
        _add_image2db(new_file_path, "visible")

    return 0
