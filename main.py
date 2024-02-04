from nbt_monitor import NBTMonitor

with NBTMonitor(("localhost", 25575), "very_secure_password") as monitor:
    while True:
        monitor.wait()
        for player, data in monitor.data.items():
            with open(player + ".json", "w") as file:
                file.truncate()
                file.write(data.model_dump_json(indent=4))