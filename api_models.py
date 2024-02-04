from pydantic import BaseModel
from nbt_monitor import NBTInfo

class LocationInfo(BaseModel):
    position: tuple[float, float, float]
    motion: tuple[float, float, float]
    dimension: str
    on_ground: bool
    rotation: tuple[float, float]
    
    @staticmethod
    def from_nbtinfo(info: NBTInfo) -> "LocationInfo":
        return LocationInfo(
            position=info.position,
            motion=info.motion,
            dimension=info.dimension,
            on_ground=info.on_ground,
            rotation=info.rotation
        )
