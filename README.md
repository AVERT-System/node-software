<h1 align="center">
    <b>NOTE: THIS PACKAGE IS A WORK IN PROGRESS</b>
</h1>

# The AVERT System hub/node software
The [AVERT](https://vulcan1.ldeo.columbia.edu) instrument platform is an attempt to draw together the plethora of existing instrumentation for volcanological observations (e.g. seismometers, GNSS antennas/receivers, cameras, etc) and the potential for edge-computing for rapid data analysis and smart data telemetry.

An early version of the system is currently deployed at Cleveland volcano in the remote Aleutian island chain, where data are being telemetered back via a satellite uplink (BGAN) to our data server at the Lamont-Doherty Earth Observatory.

The system is composed of a number of layers:

1. System-level configuration, such as configuring the network interfaces and system daemons for managing data acquisition and telemetry
2. A data acquisition system (a stand-alone Python package)
3. Auxiliary control system, which confers the ability to autonomously control the power to various physical components inside the box e.g. operating the radio/network relay in burst mode

## Installation
The data acquisition package requires a minimum Python version of 3.11—this is the default distribution installed with Debian 12 (Bookworm), which is the operating system used by the single-board computers (SBCs).

The ultra-lightweight `venv` package is used on the SBCs to isolate the system software (and its dependencies) from the system-wide Python installation. If building from source on a new SBC, be sure to create a virtual environment before installing. If testing the system on some other  The hub/node software can be installed by cloning this repository, navigating into the `data-acquisition` directory (`cd data-acquisition`) and running `pip install .`. It is not currently registered on the Python Package Index (nor is there any plan to do so in the near future).

Note: This requires an internet connection.

## Configuring a node
Once the system software is installed, configuration files must be installed using the `avert-config` command-line tool, e.g.:

```
avert-config install -c <config_file> -t <network>
avert-config install -c <config_file> -t <node>
```

Example config files will be added soon.

## Futures
Extension to include drivers for a broader range of existing instrumentation systems. `systemd` service files will also be added for each of the 

## Contact
You can contact us directly at: avert-system [ at ] proton.me

Any additional comments/questions can be directed to:
* **Conor Bacon** - cbacon [ at ] ldeo.columbia.edu

## License
This package is written and maintained by the AVERT System Team, Copyright AVERT System Team 2023. It is distributed under the GPLv3 License. Please see the [LICENSE](LICENSE) file for a complete description of the rights and freedoms that this provides the user.
