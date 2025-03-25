#!/bin/bash

REPO_PATH="/opt/BalancaPubRepo"
CMD_INICIAR="python3 $REPO_PATH/bin/app/main.py"
LOG_FILE="/tmp/monitor.log"
onehour=3600

while true; do
    if ! pgrep -f "python3 $REPO_PATH/bin/app/main.py" > /dev/null; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - [Monitor] Starting app..." | tee -a "$LOG_FILE"
        $CMD_INICIAR &
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - [Monitor] App is running." | tee -a "$LOG_FILE"
    fi
    sleep "$onehour"
done