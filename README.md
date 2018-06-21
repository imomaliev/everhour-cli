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
everhour
# list your tasks
> list
# start time on task
> start task_id
# stop
> stop
```
