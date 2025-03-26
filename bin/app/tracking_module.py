import os
import time
import requests
from datetime import datetime, timezone


URL_SERVER = "https://7948-170-80-64-72.ngrok-free.app/IoT/Balanca/status"
DEVICE_PATH = '/etc/device_id'

class tracking():
    def enviar_dados(self):
        global NUMERO_SERIAL
        if os.path.exists(DEVICE_PATH):
            with open(DEVICE_PATH, 'r') as f:
                NUMERO_SERIAL = f.read().strip()
        dados = f'{NUMERO_SERIAL};Dispositivo online;{datetime.now(timezone.utc)}'
        texto_byte = bytes(dados, 'utf-8')
        headers = {"Content-Type": "application/octet-stream"}
        try:
            resposta = requests.post(URL_SERVER, data=texto_byte, headers=headers)
            print(f"[Tracking] Dados enviados: {resposta.status_code} - {resposta.text}")
        except Exception as e:
            print(f"[Tracking] Falha ao enviar dados: {e}")

# if __name__ == "__main__":
#     while True:
#         enviar_dados()
#         time.sleep(90)  # Espera 1:30 min antes de enviar de novo
