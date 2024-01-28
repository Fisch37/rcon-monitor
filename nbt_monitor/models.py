from enum import IntEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel
import nbtlib

from rcon_monitor import PlayerInfo
from nbt_monitor.utils import ConvertsNBT, Assignment, nbt_to_primitive


class InventorySlot(ConvertsNBT, BaseModel):
    __ASSIGNMENT_TABLE__ = {
        "slot": Assignment("Slot"),
        "id": Assignment("id"),
        "count": Assignment("Count"),
        "tag": Assignment("tag", optional=True, default_factory=lambda: {})
    }
    
    slot: int
    id: str
    count: int
    tag: dict|None


class Modifier(ConvertsNBT, BaseModel):
    class ModifierOperation(IntEnum):
        ADD = 0
        MULTIPLE_BASE = 1
        MULTIPLY = 2
    
    __ASSIGNMENT_TABLE__ = {
        "amount": Assignment("Amount"),
        "operation": Assignment(
            "Operation",
            ModifierOperation
        ),
        "uuid": Assignment(
            "UUID",
            lambda raw: UUID(bytes=b"".join(
                s32.to_bytes(4, signed=True)
                for s32 in raw
            ))
        ),
        "name": Assignment("Name")
    }
    
    amount: float
    operation: ModifierOperation
    uuid: UUID
    name: str

class Attribute(ConvertsNBT, BaseModel):
    __ASSIGNMENT_TABLE__ = {
        "base_value": Assignment("Base"),
        "name": Assignment("Name"),
        "modifiers": Assignment(
            "Modifiers",
            nbt_converter=lambda nbt: [
                Modifier.from_nbt(subnbt) for subnbt in nbt
            ],
            optional=True,
            default_factory=lambda: []
        )
    }
    base_value: float
    name: str
    modifiers: list[Modifier]

class Gamemode(IntEnum):
    SURVIVAL = 0
    CREATIVE = 1
    ADVENTURE = 2
    SPECTATOR = 3


def _parse_inventory(nbt: nbtlib.List) -> list[InventorySlot]:
    return [
        InventorySlot.from_nbt(slot)
        for slot in nbt
    ]


class NBTInfo(PlayerInfo):
    __CUSTOM_ASSIGNMENTS__ = {
        "inventory": Assignment("Inventory", nbt_converter=_parse_inventory),
        "enderchest": Assignment("EnderItems", nbt_converter=_parse_inventory),
        "position": Assignment("Pos", tuple),
        "dimension": Assignment("Dimension"),
        "attributes": Assignment(
            "Attributes",
            nbt_converter=lambda nbt: [
                Attribute.from_nbt(subnbt)
                for subnbt in nbt
            ]
        ),
        "gamemode": Assignment("playerGameType", Gamemode),
        "health": Assignment("Health")
    }
    
    data: dict
    inventory: list[InventorySlot]
    enderchest: list[InventorySlot]
    position: tuple[float, float, float]
    dimension: str
    attributes: list[Attribute]
    gamemode: Gamemode
    health: float
    
    @staticmethod
    def from_nbt(time: float, nbt: nbtlib.Compound) -> "NBTInfo":
        data = nbt_to_primitive(nbt)
        kwargs = {}
        for attribute, assignment in NBTInfo.__CUSTOM_ASSIGNMENTS__.items():
            kwargs[attribute] = assignment(nbt)
        
        return NBTInfo(
            time=time,
            data=data,
            **kwargs
        )