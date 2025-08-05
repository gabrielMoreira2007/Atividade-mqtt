import socket
import threading

HOST = 'localhost'
PORT = 1883
TOPIC = 'servidor/temperatura'

def ouvir_broker(sock):
    while True:
        data = sock.recv(1024)
        if not data:
            break
        print(f"📥 Recebido: {data.decode().strip()}")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Conectado ao broker MQTT")
        
        # Envia comando de inscrição no tópico
        subscribe_message = f"SUBSCRIBE:{TOPIC}"
        s.sendall(subscribe_message.encode())
        print(f"📝 Inscrito no tópico: {TOPIC}")

        # Inicia thread para escutar mensagens do broker
        thread = threading.Thread(target=ouvir_broker, args=(s,), daemon=True)
        thread.start()

        # Mantém o programa rodando
        input("Pressione ENTER para sair...\n")

if __name__ == "__main__":
    main()
