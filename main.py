from nbt_monitor import NBTMonitor

with NBTMonitor(("localhost", 25575), "very_secure_password") as monitor:
    monitor.wait()
    for player, nbt in monitor.data.items():
        print(player, "with", nbt)