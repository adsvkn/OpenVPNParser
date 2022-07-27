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
    __vpn_parsers: Dict[str, AbcSite] = {
        'vpngate': VPNGate(WORK_FOLDER)
    }

    def __init__(self, argv: List[str]) -> None:
        self.__init_conf_dir()
        self.__parser = self.__init_parser()
        self.__argv = argv
    
    def start(self) -> None:
        ns = self.__parser.parse_args(self.__argv[1:])

        if ns.list:
            self.__print_tables()
        if ns.update:
            self.__update_tables()
        if ns.table and ns.index:
            self.__connect(ns.table, ns.index)
        

    def __init_conf_dir(self) -> None:
        if not os.path.isdir(WORK_FOLDER):
            os.mkdir(WORK_FOLDER)

    def __init_parser(self) -> ArgumentParser:
        choices_vpn = self.__vpn_parsers.keys()

        parser = ArgumentParser()
        parser.add_argument('--update', '-u', dest='update',
            action='store_true', help='Update the list of VPN servers')
        parser.add_argument('--list', '-l', dest='list',
            action='store_true', help='Print a list of vpn servers')

        subparser = parser.add_subparsers()
        subparser_connect = subparser.add_parser('connect', help='Connect to VPN server')
        subparser_connect.add_argument('--table', '-t', dest='table',
            type=str, choices=choices_vpn, help='Select VPN table')
        subparser_connect.add_argument('--index', '-i', dest='index',
            type=int, help='Vpn server number')
        
        return parser

    def __print_tables(self) -> None:
        for key, value in self.__vpn_parsers.items():
            print(f'Table: {key}')
            try:
                print(value.table(), end='\n\n')
            except VPNFileNotFoundError as ex:
                print(f' Config file not found: "{ex._file_path}"\n Use the flag: "--update"', file=sys.stderr)
    
    def __update_tables(self) -> None:
        for key, value in self.__vpn_parsers.items():
            print(f'Table "{key}" updated...')
            value.update()

    def __connect(self, table: str, index: int) -> None:
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
