from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.history import FileHistory

from .api import api_map
from .completer import everhour_completer
from .history import get_history
from .subcommands import start_timer, stop_timer, list_tasks


def main():
    history = FileHistory(get_history())
    session = PromptSession('> ', completer=everhour_completer, history=history)

    while True:
        def get_prompt():
            " Tokens to be shown before the prompt. "
            if api_map.timer:
                return [
                    ('bg:#008800 #ffffff', '%s' % (api_map.timer)),
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
                start_timer(api_map, task_id)
            elif text.startswith('stop'):
                stop_timer(api_map)
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
            if api_map.timer:
                api_map.timer.stop()
            break  # Control-D pressed.


if __name__ == '__main__':
    main()
