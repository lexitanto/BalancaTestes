#!/bin/bash

MOUNT_POINT="/mnt/usb_wifi"
CONFIG_FILE="wifi_setup.txt"
DEVICE="/dev/$1"

(

    flock -w 10 200 || exit 1

    sudo systemctl daemon-reload
    [ ! -d "$MOUNT_POINT" ] && mkdir -p "$MOUNT_POINT"

    if mount -o ro "$DEVICE" "$MOUNT_POINT"; then
        WIFI_CONFIG="$MOUNT_POINT/wifi_setup.txt"

        if [ -f "$WIFI_CONFIG" ]; then
            echo "Arquivo encontrado: $WIFI_CONFIG"

            SSID=$(grep -E "^SSID=" "$WIFI_CONFIG" | cut -d '=' -f2 | tr -d ';"')
            PSK=$(grep -E "^PSK=" "$WIFI_CONFIG" | cut -d '=' -f2 | tr -d ';"')

            if [[ -n "$SSID" && -n "$PSK" ]]; then
                echo "SSID e PSK válidos encontrados."

                cat <<EOF > /etc/wpa_supplicant/wpa_supplicant.conf
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=BR

network={
    ssid="$SSID"
    psk="$PSK"
}
EOF
                echo "Wi-Fi atualizado. Reiniciando serviço..."
                systemctl restart wpa_supplicant
            else
                echo "SSID ou PSK inválidos!"
            fi
        else
            echo "Arquivo wifi_setup.txt não encontrado. Pulando partição."
        fi

        umount "$MOUNT_POINT"
        echo "Partição $1 processada e desmontada."
    else
        echo "Falha ao montar /dev/$1"
    fi


) 200>/tmp/wifi_script.lock
