from typing import Iterable
from mcipc.rcon.je import Client
from mcipc.rcon.commands.execute import ExecuteProxy
from time import monotonic
from threading import Thread, Event
from dataclasses import dataclass
from abc import ABCMeta, abstractmethod


class RconPlayerMonitor[RawPlayerInfo, PlayerInfo](Thread, metaclass=ABCMeta):
    def __init__(
        self, 
        address: tuple[str, int], 
        password: str|None=None,
        *,
        update_interval: float=0.5
    ):
        self._client = Client(*address, passwd=password)
        self._interval = update_interval
        self._stop_event = Event()
        self._data: dict[str, PlayerInfo] = {}
        self._data_event = Event()
        super().__init__(daemon=True)
    
    @abstractmethod
    def execute(self, client: Client) -> Iterable[RawPlayerInfo]: ...
    
    @abstractmethod
    def parse(self, raw: Iterable[RawPlayerInfo]) -> dict[str, PlayerInfo]: ...
    
    def run(self) -> None:
        with Client("localhost", 25575, passwd="very_secure_pswd") as client:
            while not self._stop_event.is_set():
                self._data = self.parse(self.execute(client))
                
                self._data_event.set()
                self._data_event.clear()
                self._stop_event.wait(timeout=self._interval)
    
    def stop(self) -> None:
        self._stop_event.set()
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, *args, **kwargs):
        self.stop()
        self.join()
    
    @property
    def data(self):
        return self._data
    
    def wait(self, timeout: float|None=None):
        """Wait for new data"""
        self._data_event.wait(timeout)
