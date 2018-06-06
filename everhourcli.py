import time
import datetime
import json

from pathlib import Path

from everhour import Everhour

import click
from click.utils import _default_text_stdout

from xdg import XDG_CONFIG_HOME


def get_xdg_json_data():
    path = Path(XDG_CONFIG_HOME, 'everhour', 'settings.json')
    if path.exists():
        with path.open('r') as a:
            return json.load(a)
    return {}


class Timer:
    def __init__(self, start_dt):
        self._delta = datetime.datetime.now() - start_dt

    def __repr__(self):
        return str(self._delta).split('.')[0]


@click.command()
@click.argument('task_id')
def main(task_id):
    configs = get_xdg_json_data()
    ev = Everhour(configs['token'])
    start_dt = datetime.datetime.now()
    resp = ev.timers.start(task_id)
    while True:
        try:
            time.sleep(2)
            click.echo('{0}'.format(Timer(start_dt)))
            _default_text_stdout().write('\033[F')  # Cursor up one line
        except KeyboardInterrupt:
            click.echo('Stopped', nl=True)
            resp = ev.timers.stop()
            break


if __name__ == '__main__':
    main()
