"""
Monitor for new files being acquired from instruments and shuffle them into the
relevant file archive.

:copyright:
    2024, the AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib

from avert_firmware.cli.telemeter import TELEMETRY_FN_LOOKUP
from avert_firmware.drivers.network_relay import set_relay_state
from avert_firmware.utilities import ping, read_config, rsync
from avert_firmware.data_archival import id_file_format
import inotify.adapters


def monitor_for_files():
    """
    Monitor for new files and migrate into relevant archives.

    This function creates an event loop that continuously monitors for new files being
    added to specific directories of interest. This is achieved using the Linux
    `inotify` utility. The data file type (e.g. miniSEED, JPG, etc) is subsequently
    identified before the file is migrated into the appropriate archive.

    """

    config = read_config()
    mode = config["telemetry"]["telemeter_by"]
    target_ip = config["telemetry"]["target_ip"]
    data_dir = pathlib.Path(config["data_archive"])

    i = inotify.adapters.Inotify()
    for receive_dir in data_dir.glob("*/receive/"):
        i.add_watch(str(receive_dir))
    for transmit_dir in data_dir.glob("*/transmit/"):
        i.add_watch(str(transmit_dir))

    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event
        if "IN_CLOSE_WRITE" not in type_names and "IN_MOVED_TO" not in type_names:
            continue
        
        filepath = pathlib.Path(path) / filename
        if filepath.name[0] == ".":  # temporary file for rsync pre-hash checks
            continue

        print(f"File found in {filepath.parent.name} directory:\n\t{filepath.name}")
        match filepath.parent.name:
            case "receive":
                print("   ...migrating...")
                migration_fn = id_file_format(filepath)
                if migration_fn is None:
                    continue

                archive_path = filepath.parents[1] / "ARCHIVE"

                _ = migration_fn(filepath, archive_path)

                # Sync retrieved data to transmit dir and remove from receive dir
                transmit_dir = filepath.parents[1] / "transmit"
                transmit_dir.mkdir(exist_ok=True, parents=True)
                return_code = rsync(
                    source=str(filepath),
                    destination=str(transmit_dir / filepath.name),
                    mkpath=True,
                )

                print("   ...migration complete...")
            case "transmit":
                # Check relevant telemetry equipment is present (satellite/radio transceiver)
                transceiver_ip = config["telemetry"]["transceiver_ip"]
                print(f"   ...searching for telemetry equipment at {transceiver_ip}...")
                return_code = ping(transceiver_ip)
                if return_code != 0:
                    print(
                        "      ...telemetry equipment not found, attempting to power on..."
                    )
                    return_code = set_relay_state(
                        config["relay"]["ip"],
                        config["relay"][mode],
                        1,
                    )
                    if return_code != 0:
                        print("   ...power on failed.")
                        continue

                    return_code = ping(transceiver_ip)
                    if return_code != 0:
                        print("      ...could not power telemetry equipment.")
                        continue
                print("   ...found...")
                
                filepath = pathlib.Path(path) / filename
                print("   ...telemetering...")
                return_code = TELEMETRY_FN_LOOKUP[mode](
                    filepath, target_ip, config["telemetry"]
                )
        
        print("   ...cleaning up...")
        if return_code == 0:
            filepath.unlink()
            print("   ...success.\n")

if __name__ == "__main__":
    monitor_for_files()
