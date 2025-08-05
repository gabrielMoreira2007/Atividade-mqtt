import socket
import time
import random

HOST = 'localhost'
PORT = 1883
TOPIC = 'servidor/temperatura'

def gerar_temperatura():
    return round(random.uniform(30.0, 80.0), 2)

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Conectado ao broker MQTT")

        while True:
            temperatura = gerar_temperatura()
            mensagem = f"PUBLISH:{TOPIC}:{temperatura}"
            s.sendall(mensagem.encode())
            print(f"📡 Publicado: {mensagem}")
            time.sleep(5)

if __name__ == "__main__":
    main()
