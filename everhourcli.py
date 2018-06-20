import os
import time
import datetime
import json
import textwrap
import operator

from collections import namedtuple

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
        # we need to account for long lines
        # TODO: have issues on resize
        width = os.get_terminal_size().columns
        lines = len(self.__repr__()) // width + 1
        # https://stackoverflow.com/a/5291044/3627387
        _default_text_stdout().write('\033[F\033[K' * lines)  # Cursor up one line


TimeRecord = namedtuple('TimeRecord', ('name', 'id', 'time'))


def _strfttime(seconds):
    hours, seconds = divmod(seconds, 3600)
    minutes = seconds // 60
    if not hours:
        return '{}m'.format(minutes)
    return '{}h {}m'.format(hours, minutes)


@click.command()
@click.argument('range_', default='today')
def _list(range_):
    if range_ == 'today':
        today = datetime.date.today()
        range_ = [today, today]
    elif range_ == 'week':
        today = datetime.date.today()
        start = today - datetime.timedelta(days=today.weekday())
        end = start + datetime.timedelta(days=6)
        range_ = [start, end]
    elif range_ == 'month':
        today = datetime.date.today()
        range_ = [today.replace(day=1), today.replace(day=1, month=today.month + 1) - datetime.timedelta(days=1)]

    table = set()
    total = 0
    for account, api in api_map.items():
        records = api.users.time()
        me_id = str(api.users.me()['id'])

        record_map = {}
        record_names = {}
        for record in records:
            # 2018-06-18 04:44:33
            record_date = datetime.datetime.strptime(record['date'], '%Y-%m-%d').date()
            if range_[1] >= record_date >= range_[0]:
                total += record['time']
                record_id = record['task']['id']

                if record_id not in record_map:
                    record_map[record_id] = TimeRecord(
                        name=record['task']['name'],
                        id=record['task']['id'],
                        time=record['time']
                    )
                else:
                    record_map[record_id] = record_map[record_id]._replace(time=record_map[record_id].time + record['time'])
        for k, task in record_map.items():
            task_time = _strfttime(task.time)
            row = (account, task.id, '\n'.join(textwrap.wrap(task.name, 50)), task_time)
            table.add(row)

    table = sorted(table, key=lambda i: i[0])
    total_time = _strfttime(total)
    table.append(('total', '', 'Total', total_time))
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
