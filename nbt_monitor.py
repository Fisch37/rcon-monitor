from typing import Iterable, overload

import nbtlib
from pydantic import ConfigDict

from rcon_monitor import RconPlayerMonitor, PlayerInfo, Client

PrimitiveNBT = dict[str, "PrimitiveNBT"]|list["PrimitiveNBT"]|int|float|str

# Doing overloads here because it's easy and static type checkers leave me alone then
@overload
def nbt_to_primitive(nbt: nbtlib.Compound) -> dict[str, PrimitiveNBT]: ...

@overload
def nbt_to_primitive(nbt: nbtlib.Base) -> PrimitiveNBT: ...

def nbt_to_primitive(nbt: nbtlib.Base) -> PrimitiveNBT:
    # NBT types inherit from their primitives (but pydantic doesn't like them)
    if isinstance(nbt, dict):
        return {key: nbt_to_primitive(value) for key, value in nbt.items()}
    if isinstance(nbt, list|nbtlib.Array):
        return [nbt_to_primitive(subnbt) for subnbt in nbt]
    if isinstance(nbt, int):
        return int(nbt)
    if isinstance(nbt, float):
        return float(nbt)
    if isinstance(nbt, str):
        return str(nbt)
    raise RuntimeError("Encountered unfamiliar nbt type!")

class NBTInfo(PlayerInfo):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    nbt: dict

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
            data[player] = NBTInfo(time=time, nbt=nbt_to_primitive(nbt))
        return data