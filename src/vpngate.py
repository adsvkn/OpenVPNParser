from vpnabc import (
    AbcSite, VPNError, VPNFileNotFoundError
)
import requests
import os
import csv
from prettytable import PrettyTable

class VPNGate(AbcSite):
    __url = 'http://www.vpngate.net/api/iphone/'
    __csv_name = 'vpngate.csv'
    __table_ip = 'IP'
    __table_speed = 'Speed (Mb/s)'
    __table_ping = 'Ping (ms)'
    __table_country = 'Country'

    def __init__(self, workfolder: str) -> None:
        super().__init__(workfolder)
        self.__csv_path = os.path.join(self._workfolder, self.__csv_name)

    def table(self) -> str:
        if not os.path.isfile(self.__csv_path):
            raise VPNFileNotFoundError(self.__csv_path)

        header = ['№', self.__table_country, self.__table_ip, self.__table_speed, self.__table_ping]
        table = PrettyTable(header)

        with open(self.__csv_path, 'r') as file:
            for i, items in enumerate(csv.reader(file, delimiter=',')):
                if i == 0:
                    continue
                country = items[5]
                ip = items[1]
                speed = '{0:.2f}'.format(int(items[4]) / (1024 * 1024))
                ping = items[3]
                table.add_row([i, country, ip, speed, ping])
        return str(table)

    def _download(self) -> str:
        try:
            data = requests.get(self.__url)
        except ConnectionError as ex:
            pass
        except Exception as ex:
            pass
        else:
            if not data.ok:
                pass
            return data.content.decode('utf8')
    
    def update(self) -> None:
        data = self._download()
        csv_data = '\n'.join(str(data).split('\n')[1:-2])
        with open(self.__csv_path, 'w', encoding='utf8') as file:
            file.write(csv_data)
    
if __name__ == '__main__':
    vg = VPNGate('.')
    #vg.update()
    print(vg.table())