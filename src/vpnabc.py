from abc import ABC, abstractmethod

class AbcSite(ABC):
    def __init__(self, workfolder: str) -> None:
        self.__workfolder = workfolder

    @abstractmethod
    def table(self) -> str:
        pass
    
    @abstractmethod
    def update(self) -> None:
        pass

    