#!/bin/bash

REPO_PATH="/opt/BalancaTestes"
. "$REPO_PATH/bin/config.sh"

if ! pgrep -f "python3 $REPO_PATH/bin/app/main.py" > /dev/null; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - [Monitor] Starting app..." | tee -a "$LOG_FILE"
        $CMD_INICIAR &
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - [Monitor] App is running." | tee -a "$LOG_FILE"
fi
