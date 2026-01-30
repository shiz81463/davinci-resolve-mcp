#!/bin/bash

# DaVinci Resolve MCP Server Startup Script
# This script sets up the environment and starts the MCP server

# Set DaVinci Resolve environment variables
export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Start the MCP server
echo "Starting DaVinci Resolve MCP Server..."
echo "Make sure DaVinci Resolve is running!"
python "$SCRIPT_DIR/src/main.py" "$@"
