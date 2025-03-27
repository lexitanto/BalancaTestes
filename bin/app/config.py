import os
import time
import requests
from datetime import datetime

URL_SERVER = "https://7948-170-80-64-72.ngrok-free.app/IoT/Balanca"
ENDPOINT_PAYLOAD = "/payload"
ENDPOINT_EQUIPAMENTO = "/check_equipamento"
ENDPOINT_STATUS = "/status"
PROLIFIC_PADRAO = "usb-Prolific_Technology_Inc._USB-Serial_Controller"
SERIAL_PATH = "/dev/serial/by-id"
DEVICE_PATH = "/etc/device_id"
INTERVALO_RETRY = 60
MAX_TENTATIVAS = 5
CPU_NUMBER = None
DEVICE_MODEL = None
_initialized = False

class config():
    def __init__(self):
        global CPU_NUMBER, DEVICE_MODEL, _initialized
        if not _initialized:
            CPU_NUMBER = self.get_rpi()
            DEVICE_MODEL = self.get_model()
            self.numero_serial = None
            self.check_equipamento()
            _initialized = True

    def check_equipamento(self):
        if os.path.exists(DEVICE_PATH):
            with open(DEVICE_PATH, "r") as f:
                self.numero_serial = f.read().strip()
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Config] Número serial: {self.numero_serial}")
        else:
            if CPU_NUMBER:
                try:
                    dados = f"{CPU_NUMBER};{DEVICE_MODEL}"
                    resposta = self.POST_check_equipamento(dados.encode("utf-8"), ENDPOINT_EQUIPAMENTO)
                    if resposta:
                       self.numero_serial = resposta.get("equipamento")

                    if self.numero_serial:
                        with open(DEVICE_PATH, "w") as f:
                            f.write(self.numero_serial)
                        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Config] Novo número serial salvo: {self.numero_serial}")

                except requests.RequestException as e:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Config] Erro na requisição para a API: {e}")

    def POST_check_equipamento(self, data):
        tentativas = 0
        while True:
            try:            
                headers = {"Content-Type": "application/octet-stream"}
                endpoint = URL_SERVER + ENDPOINT_EQUIPAMENTO 
                response = requests.post(endpoint, data=data, headers=headers)
                json_data = response.json()

                if response.ok:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Config] ✅ Equipamento checado com sucesso      -> {response.json()}")
                    return json_data
                else:
                    tentativas += 1
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Config] ❌ Erro ao checar o equipamento: {response.status_code}      -> {json_data}")
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Config] Tentativa {tentativas}. Nova tentativa em {INTERVALO_RETRY} segundos...")
                    time.sleep(INTERVALO_RETRY)   
                                 

            except Exception as e:
                tentativas += 1
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Config] ❌ Erro ao checar o equipamento: {e}")
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Config] Tentativa {tentativas}. Nova tentativa em {INTERVALO_RETRY} segundos...")
                time.sleep(INTERVALO_RETRY)
    def get_rpi(self):        
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line.startswith("Serial"):
                        return line.strip().split(":")[1].strip()

        except Exception as e:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Config] Erro ao ler o número de série: {e}")
            return None
        
    def get_model(self):
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line.startswith("Model"):
                        return line.strip().split(":")[1].strip()

        except Exception as e:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Config] Erro ao ler o número de série: {e}")
            return None