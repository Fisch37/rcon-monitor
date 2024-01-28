from typing import Iterable, overload, Union

import nbtlib

from rcon_monitor import RconPlayerMonitor, Client
from nbt_monitor.models import NBTInfo

class NBTMonitor(RconPlayerMonitor[str, NBTInfo]):
    def execute(self, client: Client):
        return client.run("execute as @a run data get entity @s").splitlines()
    
    def parse(self, raw: Iterable[str], time: float) -> dict[str, NBTInfo]:
        data = {}
        for line in raw:
            player_end = line.find(" ")
            if player_end == -1:
                print("WARNING Received invalid data in", repr(self))
                continue
            player = line[:player_end]
            
            nbt_start = line.find(":") + 2
            nbt: nbtlib.Compound = nbtlib.parse_nbt(line[nbt_start:])
            data[player] = NBTInfo.from_nbt(time, nbt)
        return data