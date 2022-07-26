import os
import sys
from argparse import ArgumentParser
from typing import List
from pathlib import Path
from typing import Dict
from vpnabc import AbcSite
from vpngate import VPNGate

CONF_DIR = 'ovpn.conf.d'
WORK_FOLDER = str(Path(sys.argv[0]).parent / CONF_DIR)

class VPNManager:
    __vpn_parsers: Dict[str, AbcSite] = {
        'vpngate': VPNGate(WORK_FOLDER)
    }

    def __init__(self, argv: List[str]) -> None:
        self.__init_conf_dir()
        self.__parser = self.__init_parser()
        self.__argv = argv
    
    def start(self) -> None:
        self.__parser.parse_args(self.__argv[1:])

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
            nargs=1,type=str, choices=choices_vpn, help='Select VPN table')
        subparser_connect.add_argument('--index', '-i', dest='index',
            nargs=1, type=int, help='Vpn server number')
        
        return parser
        

def main():
    vm = VPNManager(sys.argv)
    vm.start()

if __name__ == '__main__':
    main()
