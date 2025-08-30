# Tasmota Faker

A very WIP project to simulate [Tasmota][0] devices for situations around testing the REST API.

## Setup

```bash
poetry install
```

## Run single instance

```bash
poetry run flask --app server run --host 0.0.0.0 --port 5000
 ```

 ## Spawn multiple

 ```bash
 ./scripts/spawn-devices.py <num-instances>
```

[0]: https://github.com/arendst/Tasmota
