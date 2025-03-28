#!/bin/bash

DIR="/opt/BalancaTestes"
sudo apt update && sudo apt upgrade -y 

MONITOR_SERVICE="monitor.service"
MONITOR_SERVICE_PATH="/etc/systemd/system/"
MONITOR_SCRIPT="monitor.sh"
MONITOR_SCRIPT_PATH="${DIR}/bin/"

sudo chmod +x "${MONITOR_SCRIPT_PATH}${MONITOR_SCRIPT}"

sudo tee "${MONITOR_SERVICE_PATH}${MONITOR_SERVICE}" > /dev/null <<EOF
[Unit]
Description=Iniciar o aplicativo no boot do sistema
After=gitfetch.service
Wants=gitfetch.service

[Service]
Type=simple
User=root
ExecStartPre=/bin/chmod +x ${MONITOR_SCRIPT_PATH}${MONITOR_SCRIPT}
ExecStart=${MONITOR_SCRIPT_PATH}${MONITOR_SCRIPT}
WorkingDirectory=${MONITOR_SCRIPT_PATH}
StandardOutput=journal
StandardError=journal
Restart=always
RestartSec=10s

[Install]
WantedBy=multi-user.target
EOF

PENDRIVE_RULE="99-pendrive.rules"
PENDRIVE_RULE_PATH="/etc/udev/rules.d/"
PENDRIVE_SCRIPT_PATH="${DIR}/bin/wificonfig.sh"

sudo chmod +x "$PENDRIVE_SCRIPT_PATH"

sudo tee "$PENDRIVE_RULE_PATH$PENDRIVE_RULE" > /dev/null <<EOF
SUBSYSTEM=="block", ACTION=="add", ENV{ID_FS_TYPE}!="", RUN+="/bin/bash $PENDRIVE_SCRIPT_PATH %k >> /tmp/wificonfig.log 2>&1"
EOF

sudo systemctl daemon-reload
sudo systemctl enable "$MONITOR_SERVICE"
sudo udevadm control --reload-rules

echo "✅ Serviço monitor.service criado e iniciado com sucesso!"
echo "✅ Rules pendrive.rules criadas com sucesso!"

echo "O sistema será reiniciado agora!"
sleep 3

sudo reboot


# Atualizaçções passadas 
#GIT FETCH FOI IMPLEMENTADO NO .img

# GITFETCH_SERVICE="gitfetch.service"
# GITFETCH_SERVICE_PATH="/etc/systemd/system/"
# GITFETCH_SCRIPT="gitfetch.sh"
# GITFETCH_SCRIPT_PATH="/opt/BalancaTestes/bin/"

# sudo chmod +x "${GITFETCH_SCRIPT_PATH}${GITFETCH_SCRIPT}"

# sudo tee "${GITFETCH_SERVICE_PATH}${GITFETCH_SERVICE}" > /dev/null <<EOF
# [Unit]
# Description=Atualiza o repositório em todo boot
# After=network-online.target
# Wants=network-online.target

# [Service]
# Type=oneshot
# User=root
# ExecStartPre=/bin/chmod +x ${GITFETCH_SCRIPT_PATH}${GITFETCH_SCRIPT}
# ExecStart=${GITFETCH_SCRIPT_PATH}${GITFETCH_SCRIPT}

# [Install]
# WantedBy=multi-user.target
# EOF