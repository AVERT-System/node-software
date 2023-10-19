# -*- coding: utf-8 -*-
"""
This script performs the transmission of data captured on the node to the
primary hub.

"""

import pathlib
import subprocess


def main():
    data_dir = pathlib.Path("/home/auser/data/Doas")
    transmit_dir = data_dir / "txDoas"
    max_file_count = 8

    files = sorted(transmit_dir.glob("*"), reverse=True)

    if len(files) == 0:
        print("No files to be transmitted.")
        return

    for file_ in files[:max_file_count]:
        return_code = subprocess.run(
            [
                *["sshpass", "-p", "avert20"],
                *["rsync", "-av", "--remove-source-files"],
                *[file_, "auser@198.18.41.85:/home/auser/data/Doas/rDoas/"],
            ]
        ).returncode

        if return_code != 0:
            print(
                f"{file_.name} failed to send, returned code {return_code}. Continuing."
            )


if __name__ == "__main__":
    main()
