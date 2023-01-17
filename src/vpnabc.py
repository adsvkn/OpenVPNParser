from abc import ABC, abstractmethod

class VPNError(Exception):
    pass

class VPNFileNotFoundError(VPNError):
    """ Ошибка ovpn-файла конфигурации """
    def __init__(self, file_path: str, message: str = None) -> None:
        self._message = f'VPN file not found: "{file_path}"' if message is None else message
        self._file_path = file_path
        super().__init__()

class AbcSite(ABC):
    """ Интерфейс взаимодействия с сайтов vpn серверов """
    def __init__(self, workfolder: str) -> None:
        self._workfolder = workfolder

    @abstractmethod
    def table(self) -> str:
        """ Полеучение строки, в которой содержится таблица
            с vpn серверами.

            Пример:
            Table: vpngate
            +---+---------+----+--------------+-----------+
            | № | Country | IP | Speed (Mb/s) | Ping (ms) |
            +---+---------+----+--------------+-----------+
            ...
            +---+---------+----+--------------+-----------+

        """
        pass
    
    @abstractmethod
    def update(self) -> None:
        """ Обновление списка vpn серверов """
        pass

    @abstractmethod
    def get_config(self, index: int) -> str:
        """ Получение полного пути до конфигурационного ovpn-файла
            заданного по индексу (index) сервера из таблицы
        """
        pass

    