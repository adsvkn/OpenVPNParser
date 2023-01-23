# OpenVPNParser

Консольная программа, предназначеннная для обработки доступных OpenVPN серверов с различных сайтов, а также последующего подключения к OpenVPN серверам.

На текущий момент доступны OpenVPN сервера со следующих сайтов:

* [vpngate](https://www.vpngate.net/)
* [freevpn](https://freevpn.me/accounts/)
* [ipspeed](https://ipspeed.info/freevpn_openvpn.php)

## Содержание

- [OpenVPNParser](#openvpnparser)
  - [Содержание](#содержание)
  - [Порядок использования программы](#порядок-использования-программы)
  - [Пример использования программы](#пример-использования-программы)
  - [Добавление нового сайта с OpenVPN серверами](#добавление-нового-сайта-с-openvpn-серверами)

## Порядок использования программы

1. Клонировать проект командой:
   
    ``` bash
    $ git clone https://github.com/adsvkn/OpenVPNParser.git
    ```

2. Перейти в директорию OpenVPNParser

    ``` bash
    $ cd OpenVPNParser
    ```

3. Запустить программу

    ``` bash
    $ python3 ./src/vpnmgr.py --help  
    usage: vpnmgr.py [-h] [--update] [--list] {connect} ...

    positional arguments:
      {connect}
        connect     Connect to VPN server

    options:
      -h, --help    show this help message and exit
      --update, -u  Update the list of VPN servers
      --list, -l    Print a list of vpn servers
    ```

## Пример использования программы

1. Обновления списка OpenVPN серверов
   
    ``` bash
    $ python3 ./src/vpnmgr.py --update
    ```

2. Вывод списка доступных VPN серверов
   
    ``` bash
     $ python3 ./src/vpnmgr.py --list
   ```

3. Подключение к OpenVPN серверу
   
    ``` bash
    $ python3 ./src/vpnmgr.py connect --table vpngate -i 1 
    ```

## Добавление нового сайта с OpenVPN серверами

Для того, чтобы добавить новый сайт с OpenVPN серверами, необходимо выполнить 3 шага:

1. Создать *py* файл в директории [src](./src)

2. В созданном ранее файле создать класс и унаследовать его от интерфейса AbcSite и переопределить три метода

    ``` python3
    from vpnabc import AbcSite

    class VPNExample(AbcSite):

    def __init__(self, workfolder: str) -> None:
        super().__init__(workfolder)

    def table(self) -> str:
        ...

    def update(self) -> None:
        ...

    def get_config(self, index: int) -> str:
        ...
    ```

3. Затем добавить созданный класс в список в файле [vpnmgr.py](./src/vpnmgr.py)

    ``` python3
    ...

    class VPNManager:
    """ Менеджер, управляющий всеми парсерами """

    # Список доступных сайтовс vpn серверами
    __vpn_parsers: Dict[str, AbcSite] = {
        'vpngate': VPNGate(WORK_FOLDER),
        'example': VPNExample(WORK_FOLDER)
    }

    ...
    ```