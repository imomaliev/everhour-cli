import time
import datetime
import json
import textwrap

from pathlib import Path

import click
from click.utils import _default_text_stdout

from xdg import XDG_CONFIG_HOME

import tabulate

from everhour import Everhour


def get_xdg_json_data():
    path = Path(XDG_CONFIG_HOME, 'everhour', 'settings.json')
    if path.exists():
        with path.open('r') as a:
            return json.load(a)
    return {}


configs = get_xdg_json_data()
api_map = {k: Everhour(v) for k,v in configs.items()}


class Timer:
    def __init__(self, account, api, name, start_dt):
        self._account = account
        self._api = api
        self._name = name
        self._start_dt = start_dt
        self._delta = datetime.datetime.now() - self._start_dt

    def __repr__(self):
        return '{0}: {1}'.format(self._name, str(self._delta).split('.')[0])

    def __enter__(self):
        return self

    def __exit__(self, exc, value, traceback):
        click.echo('Stopped', nl=True)
        resp = self._api.timers.stop()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            self._delta = datetime.datetime.now() - self._start_dt
            time.sleep(2)
        except KeyboardInterrupt:
            raise StopIteration

    def echo(self, ):
        click.echo(self)
        # https://stackoverflow.com/a/5291044/3627387
        _default_text_stdout().write('\033[F\033[K')  # Cursor up one line


@click.command()
def _list():
    table = set()
    for account, api in api_map.items():
        tasks = api.users.time()
        me_id = str(api.users.me()['id'])

        for task in tasks:
            task = task['task']
            if task['status'] == 'completed':
                continue
            try:
                seconds = task['time']['users'][me_id]
            except KeyError:
                continue
            task_time = time.strftime("%H:%M:%S", time.gmtime(seconds))
            name = task['name']

            row = (account, task['id'], '\n'.join(textwrap.wrap(name, 50)), task_time)
            table.add(row)

    click.echo(tabulate.tabulate(
        table,
        ['account', 'id', 'name', 'time'],
        # floatfmt='.2f',
        tablefmt='grid'
    ))


@click.command()
@click.argument('task_id')
def _start(task_id):
    start_dt = datetime.datetime.now()
    for account, api in api_map.items():
        resp = api.timers.start(task_id)
        try:
            name = resp['task']['name']
            break
        except KeyError:
            continue
    with Timer(account, api, name, start_dt) as timer:
        for __ in timer:
            timer.echo()


@click.group()
def main():
    pass


main.add_command(_list, name='list')
main.add_command(_start, name='start')

if __name__ == '__main__':
    main()
