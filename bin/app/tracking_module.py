import time
import requests

URL_SERVER = "https://9271-170-80-64-72.ngrok-free.app/IoT/Balanca"

def enviar_dados():
    dados = {"mensagem": "Olá, servidor!", "timestamp": time.time()}
    try:
        resposta = requests.post(URL_SERVER, json=dados)
        print(f"[Tracking] Dados enviados: {resposta.status_code} - {resposta.text}")
    except Exception as e:
        print(f"[Tracking] Falha ao enviar dados: {e}")

if __name__ == "__main__":
    while True:
        enviar_dados()
        time.sleep(90)  # Espera 1:30 min antes de enviar de novo
