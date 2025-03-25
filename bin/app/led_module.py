import os
import time
import threading
import RPi.GPIO as GPIO
from datetime import datetime

class led():
    def __init__(self, pin_vermelho=16, pin_amarelo=20, pin_verde=21):        
        self.led_internet = pin_vermelho
        self.led_config_ext = pin_amarelo
        self.led_evento_balanca = pin_verde
        self.blinking = {self.led_internet: False, self.led_config_ext: False, self.led_evento_balanca: False}
        self.setup_gpio()

    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.led_internet, GPIO.OUT)
        GPIO.setup(self.led_config_ext, GPIO.OUT)        
        GPIO.setup(self.led_evento_balanca, GPIO.OUT)

    def _piscar_led(self, led, intervalo=1):
        while self.blinking[led]:
            GPIO.output(led, GPIO.HIGH)
            time.sleep(intervalo)
            GPIO.output(led, GPIO.LOW)
            time.sleep(intervalo)

    def start_blinking(self, led, intervalo=1):
        if not self.blinking[led]:
            self.blinking[led] = True
            t = threading.Thread(target=self._piscar_led, args=(led, intervalo), daemon=True)
            t.start()

    def stop_blinking(self, led):
        self.blinking[led] = False

    def acender_led(self, led):
        self.stop_blinking(led)
        GPIO.output(led, GPIO.HIGH)

    def desligar_led(self, led):
        self.stop_blinking(led)
        GPIO.output(led, GPIO.LOW)

    def run(self):
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [LED] Loop iniciado.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.cleanup()

    def cleanup(self):
        for led in self.blinking.keys():
            self.stop_blinking(led)
        GPIO.cleanup()
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [LED] GPIO limpo e LEDs desligados.")

    def monitor(self, intervalo=1):
        while True:
            if not self._service_is_running():
                self.start_blinking(self.led_internet, intervalo=intervalo)
            else:
                self.stop_blinking(self.led_internet)
            time.sleep(intervalo)

    def _service_is_running(self):
        status = os.system(f"systemctl is-active --quiet monitor.service")
        return status == 0