#! /bin/bash

mkdir assets
curl 'https://raw.githubusercontent.com/pubg/api-assets/master/dictionaries/telemetry/damageCauserName.json' > ./assets/damageCauserName.json
curl 'https://raw.githubusercontent.com/pubg/api-assets/master/dictionaries/telemetry/mapName.json' > ./assets/mapNames.json

python -m tasks.find_and_send_matches