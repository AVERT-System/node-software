"""
This module contains handlers for each of the subcommands accessible via the `avertctl`
command-line utility.

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

from .query_handler import query_handler
from .config_handler import config_handler
from .telemeter import telemeter_data


__all__ = [query_handler, config_handler, telemeter_data]
