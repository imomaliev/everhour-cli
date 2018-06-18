# everhour-cli
Everhour timer CLI

## Installation
```sh
pip install --process-dependency-links git+https://github.com/imomaliev/everhour-cli.git
```

## Usage
Place settings file in `XDG_CONFIG_HOME/everhour/settings.json`
```json
{
  "token": "your-token"
}

```

and then

```sh
# list your tasks
everhour list
# start time on task
everhour start task_id
# ^-c - to stop
```
