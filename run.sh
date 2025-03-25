#!/bin/bash

USER=$(logname)
MONITOR_SERVICE="/etc/systemd/system/monitor.service"
MONITOR_SCRIPT_PATH="/opt/BalancaPubRepo/bin/_monitor.sh"

sudo chmod +x "$MONITOR_SCRIPT_PATH"

sudo tee "$MONITOR_SERVICE" > /dev/null <<EOF
[Unit]
Description=Iniciar o aplicativo no boot do sistema
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=$MONITOR_SCRIPT_PATH
WorkingDirectory=/opt/BalancaPubRepo/bin/
Restart=always
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

WIFICONFIG_SERVICE="/etc/systemd/system/wifi-setup-monitor.service"
WIFICONFIG_SCRIPT_PATH="/opt/BalancaPubRepo/bin/_wificonfig.sh"

sudo chmod +x "$WIFICONFIG_SCRIPT_PATH"

sudo tee "$WIFICONFIG_SERVICE" > /dev/null <<EOF
[Unit]
Description=Monitoramento de USB para Configuração de Wi-Fi
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash $WIFICONFIG_SCRIPT_PATH
Restart=always
User=root
StandardOutput=append:/tmp/usb_wifi_monitor.log
StandardError=append:/tmp/usb_wifi_monitor_error.log

[Install]
WantedBy=multi-user.target
EOF


sudo systemctl daemon-reload
sudo systemctl enable monitor.service
sudo systemctl enable wifi-setup-monitor.service

echo "✅ Serviço _monitor.* criado e iniciado com sucesso!"
echo "✅ Serviço _wifi-setup-monitor.* criado e iniciado com sucesso!"

echo "O sistema será reiniciado agora!"
sleep 3

sudo reboot
