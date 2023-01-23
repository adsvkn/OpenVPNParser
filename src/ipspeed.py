#pylint: disable=invalid-name
""" VPNGate """
import os
import csv
import requests
from urllib.request import urlretrieve
from typing import List
from zipfile import ZipFile, ZipInfo
from base64 import b64decode, b64encode
from bs4 import BeautifulSoup
from bs4.element import Tag
from prettytable import PrettyTable
from vpnabc import (
    AbcSite, VPNFileNotFoundError
)

class IPSpeedVPN(AbcSite):
    """ Класс - парсер VPN серверов с сайта freevpn.me """
    __base_url = 'https://ipspeed.info'
    __url = f'{__base_url}/freevpn_openvpn.php'
    __csv_name = 'ipspeedvpn.csv'
    __csv_delimeter = ','

    def __init__(self, workfolder: str) -> None:
        super().__init__(workfolder)
        self.__csv_path = os.path.join(self._workfolder, self.__csv_name)

    def table(self) -> str:
        """ Получение таблицы vpn серверов

        Raises:
            VPNFileNotFoundError: Отсутствует файл со списком vpn серверов

        Returns:
            str: таблица vpn-серверов
        """
        if not os.path.isfile(self.__csv_path):
            raise VPNFileNotFoundError(self.__csv_path)

        header = ['№', 'Country', 'IP', 'Type', 'Port', 'Uptime', 'Ping']

        table = PrettyTable(header)

        with open(self.__csv_path, 'r') as file:
            for i, items in enumerate(csv.reader(file, delimiter=self.__csv_delimeter)):
                if i == 0:
                    continue

                table.add_row([i] + items[:-1])
        return str(table)

    def update(self) -> None:
        """ Обновление данных о vpn серверах """
        self._download()

    def _download(self) -> str:
        page = requests.get(self.__url)
        soup = BeautifulSoup(page.text, 'html.parser')
        server_list: List[Tag] = soup.find_all('div', class_='list')

        # извлечение стран
        countries_list = [content.contents[0] for content in server_list[4::4]]
        # извлечение времени работы
        uptime_list = [content.contents[0] for content in server_list[6::4]]
        # извлечение задержки
        ping_list = [content.contents[0] for content in server_list[7::4]]
        # извлечение ссылок на скачивание файлов конфигураций
        href_list = [[href.attrs['href'] for href in content.contents[::2]]
                    for content in server_list[5::4]]
        href_list = [[f'{self.__base_url}{href}' for href in contents] for contents in href_list]
        
        # скачивание файлов конфигураций
        with open(self.__csv_path, 'w') as file:
            writer = csv.writer(file, delimiter=self.__csv_delimeter)

            for country, href, uptime, ping in \
                zip(countries_list, href_list, uptime_list, ping_list):

                for ref in href:
                    ip, type, port = ref.split('_')
                    port = port.split('.')[0]
                    ip = ip.split('/')[-1]

                    ovpn_page = requests.get(ref)
                    base64_ovpn_data = b64encode(ovpn_page.text.encode('utf8'))

                    writer.writerow([country, ip, type, port, uptime, ping, base64_ovpn_data])
    
    def get_config(self, index: int) -> str:
        """ Получение полного пути до ovpn-файла

        Args:
            index (int): индекс vpn сервера из таблицы

        Returns:
            str: полный путь до ovpn-файла с конигурацией vpn сервера
        """
        return self._decode_config(index)

    def _decode_config(self, index: int) -> str:
        """ Декодирование конфигурации заданного vpn сервера

        Args:
            index (int): индекс vpn сервера из таблицы

        Raises:
            VPNFileNotFoundError: не найден файл с конфигурациями vpn серверов
            IndexError: неверный индекс vpn сервера

        Returns:
            str: полный путь до ovpn-файла с конигурацией vpn сервера
        """
        if not os.path.isfile(self.__csv_path):
            raise VPNFileNotFoundError(self.__csv_path)

        vpn_cfg_path = os.path.join(self._workfolder, f'ipspeed-{str(index)}.ovpn')

        with open(self.__csv_path, 'r') as file:
            lines = file.readlines()

            if not 0 < index < len(lines):
                raise IndexError()

            base64_data = lines[index].split(self.__csv_delimeter)[-1]
            decode_data = b64decode(base64_data).decode('utf8')

        with open(vpn_cfg_path, 'w') as file:
            file.write(decode_data)

        return vpn_cfg_path

if __name__ == '__main__':
    fv = IPSpeedVPN('./src/ovpn.conf.d')
    fv._download()
