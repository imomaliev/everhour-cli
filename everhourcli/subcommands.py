import datetime
import textwrap

from collections import namedtuple

import tabulate

from prompt_toolkit.shortcuts import print_formatted_text


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



TimeRecord = namedtuple('TimeRecord', ('name', 'id', 'time'))


def _strfttime(seconds):
    hours, seconds = divmod(seconds, 3600)
    minutes = seconds // 60
    if not hours:
        return '{}m'.format(minutes)
    return '{}h {}m'.format(hours, minutes)



def list_tasks(api_map, range_):
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
    print_formatted_text(tabulate.tabulate(
        table,
        ['account', 'id', 'name', 'time'],
        # floatfmt='.2f',
        tablefmt='grid'
    ))


def stop_timer(timer):
    if timer:
        timer.stop()
        print_formatted_text('Stopped')
        timer = None
    else:
        print_formatted_text('No active timer')
    return timer


def start_timer(api_map, timer, task_id):
    start_dt = datetime.datetime.now()
    for account, api in api_map.items():
        resp = api.timers.start(task_id)
        try:
            name = resp['task']['name']
            break
        except KeyError:
            continue
    return Timer(account, api, name, start_dt)
