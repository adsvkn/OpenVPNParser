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

class FreeVPN(AbcSite):
    """ Класс - парсер VPN серверов с сайта freevpn.me """
    __url = 'https://freevpn.me/accounts/'
    __zip_name = 'freevpn.zip'
    __csv_name = 'freevpn.csv'
    __csv_delimeter = ','

    def __init__(self, workfolder: str) -> None:
        super().__init__(workfolder)
        self.__csv_path = os.path.join(self._workfolder, self.__csv_name)
        self.__zip_path = os.path.join(self._workfolder, self.__zip_name)

    def table(self) -> str:
        """ Получение таблицы vpn серверов

        Raises:
            VPNFileNotFoundError: Отсутствует файл со списком vpn серверов

        Returns:
            str: таблица vpn-серверов
        """
        if not os.path.isfile(self.__csv_path):
            raise VPNFileNotFoundError(self.__csv_path)

        header = ['№', 'Country', 'Username', 'Password', 'Type', 'Port']

        table = PrettyTable(header)

        with open(self.__csv_path, 'r') as file:
            for i, items in enumerate(csv.reader(file, delimiter=self.__csv_delimeter)):
                if i == 0:
                    continue

                table.add_row([i, 'Netherland'] + items[:-1])
        return str(table)

    def update(self) -> None:
        """ Обновление данных о vpn серверах """
        self._download()

    def _download(self) -> str:
        # Скачивание zip файла с ovpn-файлами
        page = requests.get(self.__url)
        soup = BeautifulSoup(page.text, 'html.parser')
        href = soup.find('a', class_='maxbutton').attrs['href']
        urlretrieve(href, self.__zip_path)

        # Парсинг имени, пароля ...
        data: List[Tag] = soup.find_all('li')
        vpn_username: str = data[16].contents[1][1:]
        vpn_password: str = data[17].contents[1][1:]

        # Распаковка zip архива
        zip_file = ZipFile(self.__zip_path)
        
        with open(self.__csv_path, 'w', encoding='utf8') as file:
            writer = csv.writer(file, delimiter=self.__csv_delimeter)
            writer.writerow(['Username', 'Passsword', 'Type', 'Port', 'Config'])

            for file in zip_file.filelist:
                if file.is_dir():
                    continue

                if not file.filename.endswith(".ovpn"):
                    continue

                # содержимое файла конфигурации
                ovpn_data = zip_file.open(file.filename).read()
                base64_ovpn_data = b64encode(ovpn_data).decode('utf8')
                # тип соединения и порт
                vpn_type_port = file.filename.split('-')[-1].split('.')[0]
                vpn_type = vpn_type_port[:3]
                vpn_port = vpn_type_port[3:]

                writer.writerow([vpn_username, vpn_password, vpn_type, vpn_port, base64_ovpn_data])
    
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

        vpn_cfg_path = os.path.join(self._workfolder, f'freevpn-{str(index)}.ovpn')

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
    fv = FreeVPN('./src/ovpn.conf.d')
    fv._download()
