from enum import IntEnum
from uuid import UUID

from pydantic import BaseModel
import nbtlib

from rcon_monitor import PlayerInfo
from nbt_monitor.utils import ConvertsNBT, Assignment, SubmodelList, Submodel


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
        "modifiers": SubmodelList("Modifiers", Modifier, True),
    }
    base_value: float
    name: str
    modifiers: list[Modifier]


class Effect(ConvertsNBT, BaseModel):
    __ASSIGNMENT_TABLE__ = {
        "id": Assignment("id"),
        "duration": Assignment("duration"),
        "amplifier": Assignment("amplifier"),
        "show_icon": Assignment("show_icon", bool),
        "show_particles": Assignment("show_particles", bool),
        "ambient": Assignment("ambient", bool)
    }
    
    id: str
    duration: int
    amplifier: int
    show_icon: bool
    show_particles: bool
    ambient: bool


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


class LocationInfo(ConvertsNBT, BaseModel):
    __ASSIGNMENT_TABLE__ = {
        "position": Assignment("Pos", tuple),
        "motion": Assignment("Motion", tuple),
        "dimension": Assignment("Dimension"),
        "on_ground": Assignment("OnGround", bool),
        "rotation": Assignment("Rotation", tuple),
    }
    
    position: tuple[float, float, float]
    motion: tuple[float, float, float]
    dimension: str
    on_ground: bool
    rotation: tuple[float, float]


class InventoryInfo(ConvertsNBT, BaseModel):
    __ASSIGNMENT_TABLE__ = {
        "selected_slot": Assignment("SelectedItemSlot"),
        "inventory": Assignment("Inventory", nbt_converter=_parse_inventory),
        "enderchest": Assignment("EnderItems", nbt_converter=_parse_inventory),
    }
    
    selected_slot: int
    inventory: list[InventorySlot]
    enderchest: list[InventorySlot]


class SurvivalInfo(ConvertsNBT, BaseModel):
    __ASSIGNMENT_TABLE__ = {
        "health": Assignment("Health"),
        "air": Assignment("Air"),
        "fire_ticks": Assignment("Fire"),
        "effects": SubmodelList("active_effects", Effect, True),
        "food_level": Assignment("foodLevel"),
        "saturation_level": Assignment("foodSaturationLevel"),
        "exhaustion_level": Assignment("foodExhaustionLevel"),
        
        "level": Assignment("XpLevel"),
        "xp_points": Assignment("XpTotal"),
        "level_percentage": Assignment("XpP"),
    }
    
    health: float
    air: int
    fire_ticks: int
    effects: list[Effect]
    food_level: int
    saturation_level: float
    exhaustion_level: float
    
    level: int
    xp_points: int
    level_percentage: float


class NBTInfo(PlayerInfo):
    __CUSTOM_ASSIGNMENTS__ = {
        "location": Submodel(LocationInfo),
        
        "gamemode": Assignment("playerGameType", Gamemode),
        "attributes": SubmodelList("Attributes", Attribute),
        "survival": Submodel(SurvivalInfo),
        
        
        "inventory": Submodel(InventoryInfo),
        
        "recipes": Assignment("recipeBook.recipes"),
    }
    
    location: LocationInfo
    survival: SurvivalInfo
    inventory: InventoryInfo
    
    gamemode: Gamemode
    attributes: list[Attribute]
    recipes: list[str]
    
    @staticmethod
    def from_nbt(time: float, nbt: nbtlib.Compound) -> "NBTInfo":
        kwargs = {}
        for attribute, assignment in NBTInfo.__CUSTOM_ASSIGNMENTS__.items():
            kwargs[attribute] = assignment(nbt)
        
        return NBTInfo(
            time=time,
            **kwargs
        )