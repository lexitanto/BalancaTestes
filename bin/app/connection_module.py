import os
import time
import sqlite3

DB_PATH = "/opt/BalancaTestes/data/meubanco.db"

class database_connection():
    def __init__(self):
        self.conexao = None
        self.cursor = None
        self.ensure_db_exists()

    def __enter__(self):
        self.connect_to_db()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_connection()

    def ensure_db_exists(self):
        if not os.path.exists(DB_PATH):
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - [Banco] Banco de dados não encontrado, criando banco...")
            self.create_db()

    def create_db(self):
        try:
            self.conexao = sqlite3.connect(DB_PATH)
            self.cursor = self.conexao.cursor()
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS TB_UltimasTransmissoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT
                );
            """)
            self.commit()
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - [Banco] Banco de dados e tabela criados com sucesso.")
        except sqlite3.Error as e:
            print(f"[Banco] ❌ Erro ao criar o banco de dados: {e}")
        finally:
            if self.conexao:
                self.conexao.close()

    def connect_to_db(self):
        while True:
            try:
                self.conexao = sqlite3.connect(DB_PATH)
                self.cursor = self.conexao.cursor()
                print("[Banco] ✅ Conexão com o banco estabelecida.")
                break
            except sqlite3.Error as e:
                print(f"[Banco] ❌ Erro ao conectar ao banco: {e}")
                print(f"[Banco] 🔄 Tentando novamente em 90 segundos...")
                time.sleep(90)

    def close_connection(self):
        self.conexao.close() 

    def get_cursor(self):        
        return self.cursor 
    
    def salvar_transmissoes(self, data):    
        try:                      
            self.cursor.execute("""
                INSERT INTO TB_UltimasTransmissoes (data)
                VALUES (?)
                """, (data,))
            self.commit()  # Confirma a operação
            print(f"[Banco] ⚠️ Última trasmissão '{data.decode('utf-8')}' salva no banco!")

        except sqlite3.Error as e:
            print(f"[Banco] ❌ Erro ao salvar localização: {e}")

    def fetch_data(self):
        try:
            self.cursor.execute("SELECT * FROM TB_UltimasTransmissoes")  # Pega todos os registros
            registros = self.cursor.fetchall()  # Retorna uma lista de tuplas        
            return registros
        
        except sqlite3.Error as e:
            print(f"[Banco] ❌ Erro ao buscar dados: {e}")
            return None
    
    def delete_at_index(self, id):
        try:
            self.cursor.execute("""
                DELETE FROM TB_UltimasTransmissoes 
                WHERE id = ? """, (id,))
            self.commit()
            print(f"[Banco] ⚠️ Indíce [{id}] deletado da tabela.")

        except sqlite3.Error as e:
            print(f"[Banco] ❌ Erro ao deletar na tabela: {e}")

    def commit(self):
	    self.conexao.commit()   
    
    

    

