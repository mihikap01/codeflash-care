import json
import logging
import os
import subprocess
import sys
from collections import defaultdict

from plugs.plug import Plug

logger = logging.getLogger(__name__)


class PlugManager:
    """
    Manager to manage plugs in care
    """

    def __init__(self, plugs: list[Plug]):
        # Store the plugs and maintain a cached list of their names for fast lookup
        self.plugs: list[Plug] = plugs[:]
        self._plug_names_cache: list[str] = [plug.name for plug in self.plugs]

        # load additional plugs from environment variable
        additional_plugs = os.getenv("ADDITIONAL_PLUGS")
        if additional_plugs:
            try:
                plug_dicts = json.loads(additional_plugs)
                # Prepare Plug objects and extend both lists in one loop
                plug_objs = [Plug(**plug) for plug in plug_dicts]
                self.plugs.extend(plug_objs)
                self._plug_names_cache.extend(plug.name for plug in plug_objs)
            except json.JSONDecodeError:
                logger.error("ADDITIONAL_PLUGS is not a valid JSON")

    def install(self) -> None:
        packages = {f"{x.package_name}{x.version}" for x in self.plugs}
        if packages:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", *packages]
            )  # noqa: S603

    def add_plug(self, plug: Plug) -> None:
        if not isinstance(plug, Plug):
            msg = "plug must be an instance of Plug"
            raise ValueError(msg)
        self.plugs.append(plug)

    def get_apps(self) -> list[str]:
        # Return the cached list of names for O(1) performance
        return self._plug_names_cache[:]

    def get_config(self) -> defaultdict[str, dict]:
        configs: defaultdict[str, dict] = defaultdict(dict)
        for plug in self.plugs:
            if plug.configs is None:
                continue
            for key, value in plug.configs.items():
                configs[plug.name][key] = value
        return configs
