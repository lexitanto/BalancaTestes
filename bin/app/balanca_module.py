# balanca_module.py
import os
import time
import serial
import requests
from datetime import datetime
from connection_module import database_connection
from led_module import led


# Configurações
INTERVALO_RETRY = 60
MAX_TENTATIVAS = 5
PROLIFIC_PADRAO = 'usb-Prolific_Technology_Inc._USB-Serial_Controller'
DEV_PATH = '/dev/serial/by-id'
DEVICE_PATH = '/etc/device_id'
URL_SERVER = 'https://9271-170-80-64-72.ngrok-free.app/IoT/Balanca'
URL_PAYLOAD = '/payload'
URL_EQUIPAMENTO = '/check_equipamento'
DB = database_connection()
LED_CONTROL = led()
LOG_FILE = "/tmp/balanca.log"


class balanca():
    def __init__(self):
        self.serial_port = serial.Serial()
        self.check_equipamento()
        self.find_and_open_serial()

    def check_equipamento(self):
        global NUMERO_SERIAL, CPU_NUMBER, DEVICE_MODEL

        if os.path.exists(DEVICE_PATH):
            with open(DEVICE_PATH, 'r') as f:
                NUMERO_SERIAL = f.read().strip()
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] Número do equipamento carregado: {NUMERO_SERIAL}")
        else:
            CPU_NUMBER = self.get_rpi()
            DEVICE_MODEL = self.get_model()
            if CPU_NUMBER:
                try:
                    string_dados = f"{CPU_NUMBER};{DEVICE_MODEL}"
                    texto_byte = bytes(string_dados, 'utf-8')
                    response = self.POST_check_equipamento(texto_byte, URL_EQUIPAMENTO)
                    if response:
                        NUMERO_SERIAL = response.get("equipamento")
                        if NUMERO_SERIAL:
                            with open(DEVICE_PATH, 'w') as f:
                                f.write(NUMERO_SERIAL)
                            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] Novo número serial obtido e salvo: {NUMERO_SERIAL}")
                        else:
                            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] Erro: Nenhum número serial retornado pela API.")
                except requests.RequestException as e:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] Erro na requisição para a API: {e}")
            else:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] Erro: Não foi possível obter o número serial da CPU.")

    def get_rpi(self):        
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line.startswith("Serial"):
                        return line.strip().split(":")[1].strip()

        except Exception as e:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] Erro ao ler o número de série: {e}")
            return None
        
    def get_model(self):
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line.startswith("Model"):
                        return line.strip().split(":")[1].strip()

        except Exception as e:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] Erro ao ler o número de série: {e}")
            return None

    def find_and_open_serial(self):
        LED_CONTROL.start_blinking(LED_CONTROL.led_config_ext, intervalo=1.5)
        while True:
            dispositivo = self.find_prolific()
            if dispositivo:
                LED_CONTROL.stop_blinking(LED_CONTROL.led_config_ext)
                try:
                    self.serial_port.port = dispositivo
                    self.serial_port.baudrate = 9600
                    self.serial_port.timeout = 1
                    if not self.serial_port.is_open:
                        self.serial_port.open()
                        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] Conectado à porta {self.serial_port.port}.")
                        return                  
                except Exception as e:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] Erro ao abrir a porta serial: {e}")
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] Dispositivo serial não encontrado. Tentando novamente em {INTERVALO_RETRY} segundos...")
            time.sleep(INTERVALO_RETRY)

    def find_prolific(self):
        if not os.path.exists(DEV_PATH):
            return None
        dispositivos = os.listdir(DEV_PATH)
        for dev in dispositivos:
            if PROLIFIC_PADRAO in dev:
                return os.path.join(DEV_PATH, dev)
        return None

    def run(self):
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] Iniciando leitura...")
        try:
            evento_balanca = eventos_balanca()
            while True:
                linha = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                if linha:
                    self.interpret_serial(linha, evento_balanca)
        except KeyboardInterrupt:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] Leitura interrompida pelo usuário.") 

    def interpret_serial(self, linha, evento_balanca): 

        LED_CONTROL.acender_led(LED_CONTROL.led_evento_balanca)

        if '[h0][g0]' in linha:
            self.process_load(linha, evento_balanca)
        else:
            self.process_print(linha, evento_balanca)

        LED_CONTROL.desligar_led(LED_CONTROL.led_evento_balanca)

    def process_load(self, linha, evento_balanca):
        print(f"Linha de CARREGAMENTO recebida: {linha}")
        data_Evento = datetime.now()
        evento_balanca.Cod_identificador = 1
        evento_balanca.Peso_atual = linha[25:30].lstrip('0')
        evento_balanca.Peso_total = linha[44:51].lstrip('0')
        evento_balanca.DataEvento = data_Evento.strftime("%Y-%m-%d %H:%M:%S")
                        
        string_dados =(f'{NUMERO_SERIAL};{evento_balanca.Cod_identificador};'
                       f'{evento_balanca.DataEvento};{evento_balanca.Peso_atual};'
                       f'{evento_balanca.Peso_total}')
                        
        texto_byte = bytes(string_dados, 'utf-8')
        self.POST_eventos(texto_byte, URL_PAYLOAD)

    def process_print(self, linha, evento_balanca):
        if 'PCS:' in linha:
            total_de_pesagens = linha.replace('PCS:', '').replace(' ', '')
            evento_balanca.Total_de_pesagens = total_de_pesagens
        elif 'TOT' in linha:
            peso_total = linha.replace('TOT:', '').replace('kg', '').replace(' ', '').lstrip('0')
            evento_balanca.Peso_total = peso_total    
        elif 'SET' in linha:
            peso_maximo = linha.replace('SET:', '').replace('kg', '').replace(' ', '') 
            evento_balanca.Peso_maximo = peso_maximo
        elif 'CAMINHAO' in linha:
            caminhao = linha.replace('CAMINHAO:', '').replace(' ', '')
            evento_balanca.Caminhao = caminhao
        elif 'MATERIAIS' in linha:
            material = linha.replace('MATERIAIS:', '').replace(' ', '')
            evento_balanca.Produto = material
        elif 'OPER' in linha:
            operador = linha.replace('OPER:', '').replace(' ', '')
            evento_balanca.Operador = operador
        elif 'HORA' in linha:
            hora = linha.replace('HORA:', '').replace(' ', '')
        elif 'DATA' in linha:
            data = linha.replace('DATA:', '').replace(' ', '')
        elif 'NO.' in linha:
            id_pesagem = linha.replace('NO.:', '').replace(' ', '')
            evento_balanca.Id_Pesagem = id_pesagem
        elif '----------------' not in linha and 'REGISTRO PESAGEM' not in linha and 'kg' not in linha:
            usuario = linha
            evento_balanca.Usuario = usuario
        elif 'REGISTRO PESAGEM' in linha:
            evento_balanca.Cod_identificador = 2
            data_Evento = datetime.now()
            evento_balanca.DataEvento = data_Evento.strftime("%Y-%m-%d %H:%M:%S")

            string_dados = ( f"{NUMERO_SERIAL};{evento_balanca.Cod_identificador};"
                             f"{evento_balanca.DataEvento};{evento_balanca.Peso_atual};"
                             f"{evento_balanca.Peso_total};{evento_balanca.Peso_maximo};"
                             f"{evento_balanca.Total_de_pesagens};{evento_balanca.Id_Pesagem};"
                             f"{evento_balanca.Usuario};{evento_balanca.Operador};"
                             f"{evento_balanca.Caminhao};{evento_balanca.Produto}"
                            )


            texto_byte = bytes(string_dados, 'utf-8')
            self.POST_eventos(texto_byte, URL_PAYLOAD)   
    
    def POST_eventos(self, data, api_url):
        self.refatorar_eventos() 
        try:            
            headers = {"Content-Type": "application/octet-stream"}
            endpoint = URL_SERVER + api_url
            response = requests.post(endpoint, data=data, headers=headers)
            json_data = response.json() if response.headers.get("Content-Type") == "application/json" else None

            if response.ok:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] ✅ Sucesso! Eventos enviados      -> {json_data}")
            else:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] ❌ Erro ao enviar os eventos: {response.status_code}      -> {json_data}")
                self.salvar_ultimaTransmissao(data)

        except Exception as e:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] Erro ao enviar dados ao servidor: {e}")
            self.salvar_ultimaTransmissao(data)

    def refatorar_eventos(self):
        registros = self.fetch_data()
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Banco] registros: {registros}")
        if registros:
            for registro in registros:
                id_registro, data = registro
                response = self.POST_ultimasTransmissoes(data, URL_PAYLOAD)
                if not response:
                    break

                self.delete_data(id_registro)

    def POST_ultimasTransmissoes(self, data, api_url):
        try:            
            headers = {"Content-Type": "application/octet-stream"}
            endpoint = URL_SERVER + api_url
            response = requests.post(endpoint, data=data, headers=headers)
            with open(LOG_FILE, 'a') as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Retransmissao] {response}")
                    
            json_data = response.json() if response.headers.get("Content-Type") == "application/json" else None

            if response.ok:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] ✅ Sucesso! Eventos enviados      -> {json_data}")
                return True
            else:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] ❌ Erro: {response.status_code}      -> {json_data}")

        except Exception as e:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] Erro ao enviar dados ao servidor: {e}")
            with open(LOG_FILE, 'a') as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Retransmissao] {e}")

    def POST_check_equipamento(self, data, api_url):
        tentativas = 0
        while True:
            try:            
                headers = {"Content-Type": "application/octet-stream"}
                endpoint = URL_SERVER + api_url
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] TESTE ENDPOINT {endpoint}")
                response = requests.post(endpoint, data=data, headers=headers)
                json_data = response.json()

                if response.ok:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] ✅ Equipamento checado com sucesso      -> {response.json()}")
                    return json_data
                else:
                    tentativas += 1
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] ❌ Erro ao checar o equipamento: {response.status_code}      -> {json_data}")
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] Tentativa {tentativas}. Nova tentativa em {INTERVALO_RETRY} segundos...")
                    time.sleep(INTERVALO_RETRY)   
                                 

            except Exception as e:
                tentativas += 1
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] ❌ Erro ao checar o equipamento: {e}")
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Balanca] Tentativa {tentativas}/{MAX_TENTATIVAS}. Nova tentativa em {INTERVALO_RETRY} segundos...")
                time.sleep(INTERVALO_RETRY)

    def salvar_ultimaTransmissao(self, data):
        with DB:
            DB.salvar_transmissoes(data)

    def fetch_data(self):
        with DB:
            registros = DB.fetch_data()
            return registros
        
    def delete_data(self, id):
        with DB:
            DB.delete_at_index(id)

class eventos_balanca:
    def __init__(self):
        self.Peso_atual = None
        self.Peso_total = None
        self.Operador = None
        self.Caminhao = None
        self.Produto = None
        self.DataEvento = None
        self.Total_de_pesagens = None
        self.Usuario = None
        self.Id_Pesagem = None
        self.Cod_identificador = None
        self.Peso_maximo = None