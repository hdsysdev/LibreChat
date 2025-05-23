#!/bin/bash
set -e

# Set up Warp terminal integration
echo -e '\n# Auto-Warpify\n[[ "$-" == *i* ]] && printf '\''\eP$f{"hook": "SourcedRcFileForWarp", "value": { "shell": "bash", "uname": "'$(uname)'" }}\x9c'\'' ' >> ~/.bashrc

echo "Running model update script..."
./update-openrouter-models.sh

echo "Starting uvicorn server..."
exec uvicorn --factory speaches.main:create_app "$@"