# -*- coding: utf-8 -*-
"""
This module can be used to control the web relay state of 

:copyright:
    2023, The AVERT System Team.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import subprocess


class WebRelayQuadClient:
    RELAY_CHANNEL_MAP = {"sbc": 1, "gnns": 2, "seismic": 3, "radio": 4}

    def __init__(
        self, ip_address: str, username: str = "admin", password: str = "webrelay"
    ) -> None:
        self.url = f"http://{ip_address}"
        self.username = username
        self.password = password

    def set_state(self, relay_channel: str, state: int) -> None:
        """Update the state of item on a given relay channel."""

        relay = self.RELAY_CHANNEL_MAP[relay_channel]
        cmd = (
            f"curl -u '{self.username}:{self.password}' "
            f'"{self.url}/state.xml?relay{relay}State={state}"'
        )
        subprocess.run(cmd, shell=True)
