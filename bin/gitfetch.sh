#!/bin/bash

REPO_PATH="/opt/BalancaTestes"
. "$REPO_PATH/bin/config.sh"

while ! ping -c 1 8.8.8.8 &> /dev/null; do
    echo "$(date '+%Y-%m-%d %H:%M:%S') - [Update] Aguardando conexão com a internet..."
    sleep 5
done

echo "$(date '+%Y-%m-%d %H:%M:%S') - [Update] Atualizando repositório..." | tee -a "$LOG_FILE"

sudo git -C $REPO_PATH fetch origin
sudo git -C $REPO_PATH reset --hard origin/main

echo "$(date '+%Y-%m-%d %H:%M:%S') - [Update] Repositório atualizado!" | tee -a "$LOG_FILE"
