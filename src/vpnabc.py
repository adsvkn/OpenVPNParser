from abc import ABC, abstractmethod

class VPNError(Exception):
    pass

class VPNFileNotFoundError(VPNError):
    def __init__(self, file_path: str, message: str = None) -> None:
        self._message = f'VPN file not found: "{file_path}"' if message is None else message
        self._file_path = file_path
        super().__init__()

class AbcSite(ABC):
    def __init__(self, workfolder: str) -> None:
        self._workfolder = workfolder

    @abstractmethod
    def table(self) -> str:
        pass
    
    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def get_config(self, index: int) -> str:
        pass

    