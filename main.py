from typing import Annotated
from uvicorn import run
from fastapi import Depends, FastAPI, HTTPException

from nbt_monitor import NBTMonitor, NBTInfo
from nbt_monitor.models import LocationInfo, InventoryInfo


app = FastAPI()
nbt_monitor: NBTMonitor


def player_data(name: str):
    try:
        return nbt_monitor.data[name]
    except KeyError as e:
        raise HTTPException(404, "Player not found") from e

DependPlayerData = Annotated[NBTInfo, Depends(player_data)]


@app.get("/players/names")
def get_player_names() -> list[str]:
    return list(nbt_monitor.data.keys())

@app.get("/players")
def get_all_player_data() -> dict[str, NBTInfo]:
    return nbt_monitor.data

@app.get("/player/{name}")
def get_player_data(info: DependPlayerData) -> NBTInfo:
    return info

@app.get("/players/location")
def get_player_locations() -> dict[str, LocationInfo]:
    return {
        name: info.location
        for name, info in nbt_monitor.data.items()
    }

@app.get("/players/{name}/location")
def get_player_location(info: DependPlayerData) -> LocationInfo:
    return info.location

@app.get("/players/inventory")
def get_player_inventories() -> dict[str, InventoryInfo]:
    return {
        name: info.inventory
        for name, info in nbt_monitor.data.items()
    }

@app.get("/player/{name}/inventory")
def get_player_inventory(info: DependPlayerData) -> InventoryInfo:
    return info.inventory

@app.get("/players/survival")
def get_players_survival_stats() -> dict[str, SurvivalInfo]:
    return {
        name: info.survival
        for name, info in nbt_monitor.data.items()
    }

@app.get("/player/{name}/survival")
def get_player_survival_stats(info: DependPlayerData) -> SurvivalInfo:
    return info.survival


def main():
    global nbt_monitor
    nbt_monitor = NBTMonitor(("127.0.0.1", 25575), "very_secure_pswd")
    
    with nbt_monitor:
        run(app)

if __name__ == "__main__":
    main()
