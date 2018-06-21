import datetime
import textwrap

import tabulate

from prompt_toolkit.shortcuts import print_formatted_text


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

    record_map, total = api_map.tasks(*range_)
    for k, task in record_map.items():
        task_time = _strfttime(task.time)
        row = (task.account, task.id, '\n'.join(textwrap.wrap(task.name, 50)), task_time)
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


def stop_timer(api_map):
    if api_map.timer:
        api_map.stop()
        print_formatted_text('Stopped')
    else:
        print_formatted_text('No active timer')


def start_timer(api_map, task_id):
    api_map.start(task_id)
