# gps_module.py
import os
import time
import serial
import pynmea2
from led_module import led
from datetime import datetime

GPS_PADRAO = 'usb-u-blox_AG_-_www.u-blox.com_u-blox_7'
DEV_PATH = '/dev/serial/by-id'
GPS_FILE = '/tmp/gps_data.txt'
INTERVALO_RETRY = 60
LED_CONTROL = led()


class gps():
    def __init__(self):
        self.serial_port = serial.Serial()
        self.find_and_open_serial()

    def find_and_open_serial(self):
        LED_CONTROL.start_blinking(LED_CONTROL.led_config_ext, intervalo=0.5)
        while True:
            dispositivo = self.find_ublocx()
            if dispositivo:
                LED_CONTROL.stop_blinking(LED_CONTROL.led_config_ext)
                try:
                    self.serial_port.port = dispositivo
                    self.serial_port.baudrate = 9600
                    self.serial_port.timeout = 1
                    if not self.serial_port.is_open:
                        self.serial_port.open()
                        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [GPS] Conectado à porta {self.serial_port.port}.")
                        return
                except Exception as e:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [GPS] Erro ao abrir a porta serial: {e}")
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [GPS] Dispositivo serial não encontrado. Tentando novamente em {INTERVALO_RETRY} segundos...")
            time.sleep(INTERVALO_RETRY)

    def find_ublocx(self):
        if not os.path.exists(DEV_PATH):
            return None
        dispositivos = os.listdir(DEV_PATH)
        for dev in dispositivos:
            if GPS_PADRAO in dev:
                return os.path.join(DEV_PATH, dev)
        return None

    def run(self):
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [GPS] Iniciando leitura dos dados...")
        while True:
            try:
                linha = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                if linha.startswith("$GPGGA"):
                    self.process_gpgga(linha)
            except Exception as e:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [GPS] Erro na leitura: {e}")

    def process_gpgga(self, linha):
        try:
            msg = pynmea2.parse(linha)
            if msg.gps_qual > 0:
                lat = msg.latitude
                lon = msg.longitude
                alt = msg.altitude
                hora = msg.timestamp.strftime('%H:%M:%S')
                dados = f"{datetime.now().strftime('%Y-%m-%d')} {hora} | Lat: {lat} | Lon: {lon} | Alt: {alt}m\n"
                with open(GPS_FILE, 'a') as f:
                    f.write(msg)
                    f.write(dados)
                print(f"[GPS] Dados válidos gravados: {dados.strip()}")
            else:
                print("[GPS] Sem fix válido.")
        except pynmea2.ParseError:
            print("[GPS] Erro ao interpretar os dados NMEA.")
