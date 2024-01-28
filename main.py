from nbt_monitor import NBTMonitor

with NBTMonitor(("localhost", 25575), "very_secure_password") as monitor:
    monitor.wait()
    for player, data in monitor.data.items():
        print(data.model_dump_json(indent=4))