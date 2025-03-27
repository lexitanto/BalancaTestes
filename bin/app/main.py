# main.py
import time
import threading
from balanca_module import balanca
from led_module import led
from tracking_module import tracking
from config import config

def main():
    CONFIG = config()
    LED = led()
    # GPS = gps()
    # BALANCA = balanca()
    STATUS = tracking()

    # gps_thread = threading.Thread(target=GPS.run, daemon=True)
    # balanca_thread = threading.Thread(target=BALANCA.run, daemon=True)
    led_thread = threading.Thread(target=LED.monitor, daemon=True)
    status_thread = threading.Thread(target=STATUS.enviar_dados, daemon=True)

    # gps_thread.start()
    # balanca_thread.start()
    led_thread.start()
    status_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Encerrando a aplicação...")

if __name__ == "__main__":
    main()
