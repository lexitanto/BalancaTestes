#!/bin/bash

REPO_PATH="/opt/BalancaTestes"
. "$REPO_PATH/bin/config.sh"

LOG_FILE="/tmp/update_repo.log"

echo "$(date '+%Y-%m-%d %H:%M:%S') - [Update] Atualizando repositório..." | tee -a "$LOG_FILE"

sudo git -C $REPO_PATH fetch origin
sudo git -C $REPO_PATH reset --hard origin/main

echo "$(date '+%Y-%m-%d %H:%M:%S') - [Update] Repositório atualizado!" | tee -a "$LOG_FILE"
