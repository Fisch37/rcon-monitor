from uvicorn import run
from fastapi import FastAPI

from nbt_monitor import NBTMonitor, NBTInfo
from api_models import *


app = FastAPI()
nbt_monitor: NBTMonitor


@app.get("/players/names")
def get_player_names() -> list[str]:
    return list(nbt_monitor.data.keys())

@app.get("/players")
def get_all_player_data() -> dict[str, NBTInfo]:
    return nbt_monitor.data

@app.get("/players/location")
def get_player_locations() -> dict[str, LocationInfo]:
    return {
        name: LocationInfo.from_nbtinfo(info)
        for name, info in nbt_monitor.data.items()
    }


def main():
    global nbt_monitor
    nbt_monitor = NBTMonitor(("127.0.0.1", 25575), "very_secure_pswd")
    
    with nbt_monitor:
        run(app)

if __name__ == "__main__":
    main()
