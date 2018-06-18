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
api = Everhour(configs['token'])


class Timer:
    def __init__(self, start_dt):
        self._delta = datetime.datetime.now() - start_dt

    def __repr__(self):
        return str(self._delta).split('.')[0]

    def echo(self, name):
        click.echo('{0}: {1}'.format(name, self.__repr__()))
        _default_text_stdout().write('\033[F')  # Cursor up one line


@click.command()
def _list():
    tasks = api.users.time()
    me_id = str(api.users.me()['id'])

    def _get_table(tasks):
        table = set()
        for task in tasks:
            task = task['task']
            seconds = task['time']['users'][me_id]
            task_time = time.strftime("%H:%M:%S", time.gmtime(seconds))
            name = task['name']

            row = (task['id'], '\n'.join(textwrap.wrap(name, 50)), task_time)
            table.add(row)
        return table

    click.echo(tabulate.tabulate(
        _get_table(tasks),
        ['id', 'name', 'time'],
        # floatfmt='.2f',
        tablefmt='grid'
    ))


@click.command()
@click.argument('task_id')
def _start(task_id):
    start_dt = datetime.datetime.now()
    resp = api.timers.start(task_id)
    name = resp['task']['name']
    Timer(start_dt).echo(name)
    while True:
        try:
            time.sleep(2)
            Timer(start_dt).echo(name)
        except KeyboardInterrupt:
            click.echo('Stopped', nl=True)
            resp = api.timers.stop()
            break


@click.group()
def main():
    pass


main.add_command(_list, name='list')
main.add_command(_start, name='start')

if __name__ == '__main__':
    main()
