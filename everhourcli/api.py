import json
import datetime

from collections import namedtuple
from pathlib import Path

from xdg import XDG_CONFIG_HOME

from everhour import Everhour


def get_xdg_json_data():
    path = Path(XDG_CONFIG_HOME, 'everhour', 'settings.json')
    if path.exists():
        with path.open('r') as a:
            return json.load(a)
    return {}



configs = get_xdg_json_data()


TimeRecord = namedtuple('TimeRecord', ('account', 'name', 'id', 'time'))


class Timer:
    def __init__(self, account, api, name, start_dt):
        self._account = account
        self._api = api
        self._name = name
        self._start_dt = start_dt

    def __repr__(self):
        _delta = datetime.datetime.now() - self._start_dt
        return '{0}: {1}'.format(self._name, str(_delta).split('.')[0])

    def stop(self):
        self._api.timers.stop()


class Api:
    def __init__(self):
        self._map = {k: Everhour(v) for k,v in configs.items()}
        self.timer = None

    def tasks(self, start, end):
        total = 0
        record_map = {}
        for account, api in self._map.items():
            records = api.users.time()

            for record in records:
                # 2018-06-18 04:44:33
                record_date = datetime.datetime.strptime(record['date'], '%Y-%m-%d').date()
                if end >= record_date >= start:
                    total += record['time']
                    record_id = record['task']['id']

                    if record_id not in record_map:
                        record_map[record_id] = TimeRecord(
                            account=account,
                            name=record['task']['name'],
                            id=record['task']['id'],
                            time=record['time']
                        )
                    else:
                        record_map[record_id] = record_map[record_id]._replace(time=record_map[record_id].time + record['time'])

        return record_map, total

    def start(self, task_id):
        start_dt = datetime.datetime.now()
        for account, api in self._map.items():
            resp = api.timers.start(task_id)
            try:
                name = resp['task']['name']
                break
            except KeyError:
                continue
        self.timer = Timer(account, api, name, start_dt)

    def stop(self):
        self.timer.stop()
        self.timer = None


api_map = Api()
