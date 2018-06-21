import json

from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.history import FileHistory

from xdg import XDG_CONFIG_HOME


from everhour import Everhour

from .completer import everhour_completer
from .history import get_history
from .subcommands import start_timer, stop_timer, list_tasks


timer = None


def get_xdg_json_data():
    path = Path(XDG_CONFIG_HOME, 'everhour', 'settings.json')
    if path.exists():
        with path.open('r') as a:
            return json.load(a)
    return {}


configs = get_xdg_json_data()
api_map = {k: Everhour(v) for k,v in configs.items()}


def main():
    history = FileHistory(get_history())
    session = PromptSession('> ', completer=everhour_completer, history=history)

    global timer
    while True:
        def get_prompt():
            " Tokens to be shown before the prompt. "
            if timer:
                return [
                    ('bg:#008800 #ffffff', '%s' % (timer)),
                    ('', ' > ')
                ]
            return [
                ('', '> ')
            ]
        try:
            text = session.prompt(get_prompt, refresh_interval=1)
            text = text.strip()
            if text.startswith('start'):
                task_id = text.split(' ')[1]
                timer = start_timer(api_map, timer, task_id)
            elif text.startswith('stop'):
                timer = stop_timer(timer)
            elif text.startswith('list'):
                range_ = text.split(' ')
                if len(range_) > 1:
                    range_ = range_[1]
                else:
                    range_ = 'today'
                list_tasks(api_map, range_)

        except KeyboardInterrupt:
            continue  # Control-C pressed. Try again.
        except EOFError:
            if timer:
                timer.stop()
            break  # Control-D pressed.


if __name__ == '__main__':
    main()
