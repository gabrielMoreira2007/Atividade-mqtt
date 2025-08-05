import asyncio
import threading
import time
from datetime import datetime

subscriptions = {}

last_topic_message = {}

data_lock = threading.Lock()

LOG_FILE = "publisher_log.txt"

def log_publisher_data():

    while True:

        time.sleep(30)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"--- LOG EM {timestamp} ---\n"

        with data_lock:
            if not last_topic_message:
                log_entry += "Nenhuma atividade de publisher registrada no último minuto.\n"
            else:
                for topic, message in last_topic_message.items():
                    log_entry += f"Tópico: {topic} | Último Dado: {message}\n"

        try:
            with open(LOG_FILE, "a") as f:
                f.write(log_entry + "\n")
            print(f"[LOG] Dados dos publishers salvos em {LOG_FILE}")
        except IOError as e:
            print(f"[LOG] Erro ao escrever no arquivo de log: {e}")


async def handle_client(reader, writer):
 
    addr = writer.get_extra_info('peername')
    print(f"Novo cliente conectado: {addr}")

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break

            message = data.decode().strip()
            
            parts = message.split(":", 2)
            command = parts[0].upper()

            if command == "SUBSCRIBE" and len(parts) > 1:
                topic = parts[1]
                if topic not in subscriptions:
                    subscriptions[topic] = set()
                subscriptions[topic].add(writer)
                print(f"Cliente {addr} inscreveu-se no tópico '{topic}'")

            elif command == "PUBLISH" and len(parts) > 2:
                topic = parts[1]
                payload = parts[2]

                with data_lock:
                    last_topic_message[topic] = payload
                
                print(f"Mensagem recebida de {addr} no tópico '{topic}': {payload}")
                
                full_message = f"PUBLISH:{topic}:{payload}\n"

                if topic in subscriptions:

                    for subscriber in list(subscriptions[topic]):
                        if subscriber.is_closing():
                            subscriptions[topic].remove(subscriber)
                            continue
                        try:
                            subscriber.write(full_message.encode())
                            await subscriber.drain()
                        except ConnectionError:
                            print(f"Removendo subscriber desconectado: {subscriber.get_extra_info('peername')}")
                            subscriptions[topic].remove(subscriber)

    except asyncio.CancelledError:
        print(f"Conexão com {addr} cancelada.")
    finally:
        print(f"Cliente {addr} desconectado.")
        for topic in subscriptions:
            subscriptions[topic].discard(writer)
        writer.close()
        await writer.wait_closed()

async def main():

    logging_thread = threading.Thread(target=log_publisher_data, daemon=True)
    logging_thread.start()
    
    server = await asyncio.start_server(
        handle_client, '0.0.0.0', 1883)

    addr = server.sockets[0].getsockname()
    print(f'Broker MQTT com logging ativado rodando em {addr}')
    print(f'Os logs serão salvos em "{LOG_FILE}" a cada minuto.')

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBroker encerrado pelo usuário.")