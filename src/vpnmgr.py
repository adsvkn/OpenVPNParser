import os
import sys
from argparse import ArgumentParser
from typing import List
from pathlib import Path
from typing import Dict
from vpnabc import AbcSite, VPNFileNotFoundError
from vpngate import VPNGate

CONF_DIR = 'ovpn.conf.d'
WORK_FOLDER = str(Path(sys.argv[0]).parent / CONF_DIR)
OVPN_BIN = '/usr/sbin/openvpn'

class VPNManager:
    """ Менеджер, управляющий всеми парсерами """

    # Список доступных сайтовс vpn серверами
    __vpn_parsers: Dict[str, AbcSite] = {
        'vpngate': VPNGate(WORK_FOLDER)
    }

    def __init__(self, argv: List[str]) -> None:
        self.__init_conf_dir()
        self.__parser = self.__init_parser()
        self.__argv = argv
    
    def start(self) -> None:
        """ Метод, обработывающий аргументы командной строки """
        ns = self.__parser.parse_args(self.__argv[1:])
        
        # Вывод списка доступынх vpn серверов в консоль
        if ns.__dict__.get('list', False):
            self.__print_tables()
        # Обновление списка vpn серверов
        if ns.__dict__.get('update', False):
            self.__update_tables()
        # Подключение к выбранному vpn серверу
        if ns.__dict__.get('table', False) and \
            ns.__dict__.get('index', False):
            self.__connect(ns.table, ns.index)

    def __init_conf_dir(self) -> None:
        """ Создание директории с файлами конфигураций vpn серверов """
        if not os.path.isdir(WORK_FOLDER):
            os.mkdir(WORK_FOLDER)

    def __init_parser(self) -> ArgumentParser:
        """ Инициализация argparse """
        choices_vpn = self.__vpn_parsers.keys()

        parser = ArgumentParser()
        parser.add_argument('--update', '-u', dest='update',
            action='store_true', help='Update the list of VPN servers')
        parser.add_argument('--list', '-l', dest='list',
            action='store_true', help='Print a list of vpn servers')

        subparser = parser.add_subparsers()
        subparser_connect = subparser.add_parser('connect', help='Connect to VPN server')
        subparser_connect.add_argument('--table', '-t', dest='table',
            type=str, choices=choices_vpn, default=None, help='Select VPN table')
        subparser_connect.add_argument('--index', '-i', dest='index',
            type=int, default=None, help='Vpn server number')
        
        return parser

    def __print_tables(self) -> None:
        """ Вывод таблиц vpn серверов """
        for key, value in self.__vpn_parsers.items():
            print(f'Table: {key}')
            try:
                print(value.table(), end='\n\n')
            except VPNFileNotFoundError as ex:
                print(f' Config file not found: "{ex._file_path}"\n Use the flag: "--update"', file=sys.stderr)
    
    def __update_tables(self) -> None:
        """ Обновление списков vpn серверов """
        for key, value in self.__vpn_parsers.items():
            print(f'Table "{key}" updated...')
            try:
                value.update()
            except Exception as ex:
                print(ex.args, file=sys.stderr)

    def __connect(self, table: str, index: int) -> None:
        """ Подключение к выбранному vpn серверу """
        try:
            ovpn_cfg = self.__vpn_parsers[table].get_config(index)
        except VPNFileNotFoundError as ex:
            print(f' Config file not found: "{ex._file_path}"\n Use the flag: "--update"', file=sys.stderr)
        except IndexError as ex:
            print(f' Row "{index}" not found', file=sys.stderr)
        else:
            os.system(f'{OVPN_BIN} "{ovpn_cfg}"')

def main():
    vm = VPNManager(sys.argv)
    vm.start()

if __name__ == '__main__':
    main()
