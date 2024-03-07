"""
Monitor for new files being uploaded to the upload server and shuffle them into the
relevant file archive.

:copyright:
    2024, the AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import argparse
import pathlib
import sys

from avert_firmware.data_archival import id_file_format
import inotify.adapters


def migrate_files(args=None):
    """
    Monitor for new files and migrate into relevant archives.

    This function creates an event loop that continuously monitors for new files being
    added to specific directories of interest. This is achieved using the Linux
    `inotify` utility. The data file type (e.g. miniSEED, JPG, etc) is subsequently
    identified before the file is migrated into the appropriate archive.

    """

    archive = pathlib.Path(args.archive)
    if not archive.is_dir():
        print("Please provide a valid archive path.")
        sys.exit(2)

    i = inotify.adapters.Inotify()
    for monitor_dir in args.monitor:
        i.add_watch(monitor_dir)

    try:
        for event in i.event_gen(yield_nones=False):
            (_, type_names, path, filename) = event
            if "IN_CLOSE_WRITE" not in type_names:
                continue
            
            filepath = pathlib.Path(path) / filename
            print(
                f"File found in receive directory:\n\t{filepath.name}\n   Migrating..."
            )
            migration_fn = id_file_format(filepath)
            if migration_fn is None:
                continue

            return_code = migration_fn(filepath, archive, append_datatype=True)
            print("   ...cleaning up...")
            if return_code == 0:
                filepath.unlink()

            print("   ...migration complete.\n")
    except KeyboardInterrupt:
        print("...shutting down gracefully.")
        sys.exit(0)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-a",
        "--archive",
        help="Specify the path to the target archive.",
        required=True,
    )
    parser.add_argument(
        "-m",
        "--monitor",
        help="Specify a path to a directory to monitor",
        required=True,
        action="append",
    )

    args = parser.parse_args()

    migrate_files(args)
