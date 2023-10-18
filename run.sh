#!/bin/bash

SIXFAB_PATH="/opt/sixfab"
CORE_PATH="$SIXFAB_PATH/core"
MANAGER_SOURCE_PATH="$CORE_PATH/manager"

# Configure the environment
export PATH="$MANAGER_SOURCE_PATH/venv/bin:$PATH"

# Run the agent
$MANAGER_SOURCE_PATH/venv/bin/python3 $MANAGER_SOURCE_PATH/core_manager/run.py