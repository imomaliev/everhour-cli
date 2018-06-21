from prompt_toolkit.completion import WordCompleter


everhour_completer = WordCompleter([
    'list', 'start', 'stop'
], meta_dict={
    'list': 'List tasks default today, possible choices: today, week, month',
    'start': 'Start timer for task_id',
    'stop': 'Stop current timer',
}, ignore_case=True)

