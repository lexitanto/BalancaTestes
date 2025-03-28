#!/bin/bash

MOUNT_POINT="/mnt/usb_mount"
CONFIG_FILE="wifi_setup.txt"
DEVICE="/dev/$1"

LED_PIN=20
echo "$LED_PIN" > /sys/class/gpio/export
echo "out" > /sys/class/gpio/gpio$LED_PIN/direction

acender_led() {
    echo "1" > /sys/class/gpio/gpio$LED_PIN/value
}

apagar_led() {
    echo "0" > /sys/class/gpio/gpio$LED_PIN/value
}

(

    acender_led

    flock -w 10 200 || exit 1
    
    sudo systemctl daemon-reload
    [ ! -d "$MOUNT_POINT" ] && mkdir -p "$MOUNT_POINT"

    if mount | grep -q "$MOUNT_POINT"; then
        sudo umount "$MOUNT_POINT"
        sleep 1
    fi

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

    apagar_led

) 200>/tmp/wifi_script.lock
