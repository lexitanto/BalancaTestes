#!/bin/bash

REPO_PATH="/opt/BalancaTestes"
. "$REPO_PATH/bin/config.sh"

while true;do

if ! pgrep -f "python3 $REPO_PATH/bin/app/main.py" > /dev/null; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - [Monitor] Starting app..." | tee -a "$LOG_FILE"
        nohup $CMD_INICIAR > /dev/null 2>&1 &
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - [Monitor] App is running." | tee -a "$LOG_FILE"
fi

sleep "$ONEHOUR"

done

