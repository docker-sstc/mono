#!/usr/bin/env python3

from pathlib import Path
from typing import Any
import json
import logging
import os
import subprocess
import time
import traceback
import types
import urllib.error

def load_as_module(path: str):
    module = types.ModuleType("dynamic_module")
    with open(path, 'r') as file:
        raw_code = file.read()
        code = raw_code.split('if __name__ == \'__main__\':', 1)[0] # remove entry
        # for i, line in enumerate(code.splitlines()):
        #     if line.strip() == '':
        #         continue
        #     print(i + 1, line)
        exec(code, module.__dict__)
    return module

seafcli = load_as_module('/usr/bin/seaf-cli')

def get_dot_value(data, dot_path: str):
    keys = dot_path.split('.')
    for key in keys:
        if key in data:
            data = data[key]
        else:
            raise KeyError(dot_path)
    return data

def setDebug(debug: bool = True):
    level = logging.INFO
    format = '[%(asctime)s] [%(levelname)s] %(message)s'
    if debug:
        level = logging.DEBUG
        format = '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s'
    logging.basicConfig(format=format, level=level)

class App:
    def __init__(self) -> None:
        self.__rpc = None
        self.__cached_config = None
        self.__cached_token = None

        self.config_file = Path(self.__get_value('CONFIG', None, '/seafile-client/config.json'))
        debug: bool = bool(self.__get_value('DEBUG', 'debug', False))
        setDebug(debug)

        logging.debug('Instantiating...')
        self.username: str = self.__get_value('USERNAME', 'username')
        self.password: str = self.__get_value('PASSWORD', 'password')
        self.server_url: str = self.__get_value('SERVER_URL', 'server_url')
        self.totp_secret: str = self.__get_value('TOTP_SECRET', 'totp_secret', None)

        # https://help.seafile.com/syncing_client/linux-cli/#skip-ssl-certificate-verify
        self.disable_verify_certificate: bool = bool(self.__get_value('SEAFILE_DISABLE_VERIFY_CERTIFICATE', 'seafile.disable_verify_certificate', False))
        self.download_limit: int = self.__get_value('SEAFILE_DOWNLOAD_LIMIT', 'seafile.download_limit', None)
        self.upload_limit: int = self.__get_value('SEAFILE_UPLOAD_LIMIT', 'seafile.upload_limit', None)

        self.seafile_ini = Path.home().joinpath('.ccnet', 'seafile.ini')
        self.seafile_log = Path.home().joinpath('.ccnet', 'logs', 'seafile.log')
        self.seafile_events_log = Path.home().joinpath('.ccnet', 'logs', 'events.log')

        self.seafile_root_dir = Path('/seafile-client')
        self.seafile_data_dir = self.seafile_root_dir.joinpath('seafile-data')
        self.seafile_socket = self.seafile_data_dir.joinpath('seafile.sock')
        self.seafile_cli = 'seaf-cli'

    def __get_config_value(self, config_dot_path: str):
        if self.__cached_config is None:
            with self.config_file.open() as file:
                self.__cached_config = json.load(file)
        return get_dot_value(self.__cached_config, config_dot_path)

    def __get_value(self, env: None|str, config_dot_path: None|str, *args):
        if env is not None:
            # try secret first
            try:
                file = os.environ[f'{env}_FILE']
            except KeyError:
                pass
            else:
                with open(file, 'rt') as fo:
                    return fo.read()
            # try env
            try:
                return os.environ[env]
            except KeyError:
                pass
        # try config file
        if config_dot_path is not None:
            try:
                return self.__get_config_value(config_dot_path)
            except KeyError:
                pass
        # no default value means required
        if args:
            defaultValue = args[0]
        try:
            return defaultValue
        except UnboundLocalError:
            raise Exception(
                f'Env {env} is required'
            )

    def __mask_cmd(self, cmd: list, mask_opts: list) -> list:
        mask_cmd = []
        mask = False
        for x in cmd:
            if mask:
                mask_cmd.append('****')
                mask = False
                continue
            if x in mask_opts:
                mask = True
            mask_cmd.append(x)
        return mask_cmd

    def __run(self, cmd: list, **kwargs):
        logging.debug(f'run `{ subprocess.list2cmdline(cmd) }`')
        return subprocess.run(cmd, **kwargs)

    def __run_tfa(self):
        cmd = ['oathtool', '--base32', '--totp', self.totp_secret]
        mask_cmd = self.__mask_cmd(cmd, ['--totp'])
        logging.debug(f'run `{ subprocess.list2cmdline(mask_cmd) }`')
        return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()

    def __run_cli(self, cmd: list):
        cmd.insert(0, self.seafile_cli)
        mask_cmd = self.__mask_cmd(cmd, ['-p', '-a', '-e'])
        logging.debug(f'run `{ subprocess.list2cmdline(mask_cmd) }`')
        return subprocess.run(cmd)

    def __wait_until(self, f: Path):
        while not f.exists():
            logging.debug(f'Wait for the {str(f)} to be created')
            time.sleep(1)

    def __config(self):
        if self.disable_verify_certificate:
            args = types.SimpleNamespace(
                confdir=None,
                key='disable_verify_certificate',
                value=self.disable_verify_certificate
            )
            seafcli.seaf_config(args)
        if self.download_limit is not None:
            args = types.SimpleNamespace(
                confdir=None,
                key='download_limit',
                value=self.download_limit
            )
            seafcli.seaf_config(args)
        if self.upload_limit is not None:
            args = types.SimpleNamespace(
                confdir=None,
                key='upload_limit',
                value=self.upload_limit
            )
            seafcli.seaf_config(args)

    def __get_rpc_client(self):
        if self.__rpc is None:
            args = types.SimpleNamespace(
                confdir=None,
            )
            self.__rpc = seafcli.get_rpc_client(args)
        return self.__rpc

    def __get_cached_token(self):
        if self.__cached_token is None:
            seafcli.seafile_datadir = str(self.seafile_data_dir)
            tfa = self.__run_tfa()
            # https://github.com/haiwen/seahub/blob/master/seahub/api2/serializers.py#L137
            # https://github.com/haiwen/seahub/blob/master/seahub/two_factor/views/login.py#L212
            # if otp failed, could check log file: `/shared/logs/seahub.log`
            self.__cached_token = self.__debug_seafile_error(
                lambda: seafcli.get_token(self.server_url, self.username, self.password, tfa, seafcli.DEFAULT_CONF_DIR)
            )
        return self.__cached_token

    def __debug_seafile_error(self, fn):
        try:
            return fn()
        except Exception as e:
            if isinstance(e, urllib.error.HTTPError):
                try:
                    body = e.read().decode('utf-8')
                except Exception:
                    body = None
                logging.error(f'HTTPError: {e.code} {body}')
            raise

    def init(self):
        logging.info(f'Initializing...')
        if not self.seafile_ini.exists():
            logging.debug(f'{str(self.seafile_ini)} is not found')
            self.__run_cli(['init', '-d', str(self.seafile_root_dir)])
            self.__wait_until(self.seafile_ini)
        self.__run_cli(['start'])
        self.__wait_until(self.seafile_socket)
        self.__config()

    def list_remote(self):
        logging.info('Call seafcli.seaf_list_remote...')
        args = types.SimpleNamespace(
            confdir=None,
            C=None,
            server=self.server_url,
            username=self.username,
            password=self.password,
            token=self.__get_cached_token(),
            tfa=None,
            json=None,
        )
        seafcli.seaf_list_remote(args)

    def sync(self):
        logging.info(f'Synchronizing...')
        try:
            dirs = self.__get_config_value('dirs')
        except KeyError:
            logging.info(f'dirs not found in {self.config_file}')
            return
        rpc = self.__get_rpc_client()
        for row in dirs:
            uuid = row['uuid']
            path = row['path']
            repo = rpc.get_repo(uuid)
            if repo is not None:
                logging.info(f'{path} is already synced')
                continue
            Path(path).mkdir(parents=True, exist_ok=True)
            args = types.SimpleNamespace(
                confdir=None,
                C=None,
                library=uuid,
                server=self.server_url,
                username=self.username,
                password=self.password,
                token=self.__get_cached_token(),
                tfa=None,
                folder=path,
                lifpasswd=None,
            )
            if 'password' in row and row['password'] is not None:
                args.libpasswd = row['password']
            logging.info(f'Call seafcli.seaf_sync for {path} ({uuid})...')
            seafcli.seaf_sync(args)

    def status(self):
        logging.info('Call seafcli.seaf_status...')
        args = types.SimpleNamespace(
            confdir=None
        )
        seafcli.seaf_status(args)

    def tail_log(self):
        self.__run(['tail', '-f', str(self.seafile_log), str(self.seafile_events_log)])

if __name__ == '__main__':
    app = App()
    app.init()
    try:
        app.list_remote()
        app.sync()
    except Exception as e:
        print(traceback.format_exc())
    finally:
        app.status()
        app.tail_log()
