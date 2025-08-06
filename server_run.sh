#!/bin/bash
set -e
DEFAULT_PORT=5000
VENV_DIR=".venv"
API_FILENAME="api_base.py"
usage(){
  echo "Usage: $0 [PORT]"
  echo "PORT: Optional defaults to using $DEFAULT_PORT"
  exit 1
}
if [[ "$1" == "--help" || "$1" == "-h " ]]; then
  usage
fi

PORT=${1:-$DEFAULT_PORT}

#Check FastAPI is Installed
source env/bin/activate #Activate venv

if ! command -v fastapi &> /dev/null; then
  echo "Error 'fastapi' command not found. Pleasee install FastAPI using pip install fastapi[all]"
  exit 1
fi
#Run FastAPI
directory=$(pwd)
API_FILE="$directory/$API_FILENAME"
echo "Press Ctrl+C to stop the server"
fastapi dev "$API_FILE" --port "$PORT" --host "0.0.0.0"


