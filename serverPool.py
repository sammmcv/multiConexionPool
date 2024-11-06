#!/usr/bin/env python3
import socket
import threading
from queue import Queue
import time

HOST = "127.0.0.1"
PORT = 65432
BUFFER_SIZE = 1024

# Variables globales
max_players = None
connected_clients = 0
lock = threading.Lock()
threads = []  # 3. registro de los hilos de cada cliente

# queue conexiones activas y de espera
waiting_queue = Queue()

def handle_client(connection, address):
    global connected_clients
    print(f"Conectado al cliente con IP: {address}")

    try:
        # Envía mensaje de conexión activa para indicar que el cliente está listo para interactuar
        connection.sendall("Conectado, escribe 'adios' para terminar:".encode('utf-8'))
        
        while True:
            data = connection.recv(BUFFER_SIZE)
            if not data:
                print(f"{address} ha cerrado la conexión.")
                break
            print(f"Mensaje: {data.decode('utf-8')} de {address}")
            connection.sendall(f"Echo: {data.decode('utf-8')}".encode('utf-8'))
    except (ConnectionResetError, ConnectionAbortedError):
        print(f"{address} se desconectó inesperadamente.")
    finally:
        connection.close()
        with lock:
            if connected_clients > 0:
                connected_clients -= 1
                print(f"Clientes conectados actualmente: {connected_clients}/{max_players}")

def process_waiting_queue():
    global connected_clients
    while True:
        with lock:
            if max_players is not None and connected_clients < max_players and not waiting_queue.empty():
                # sacar del queue de espera y se mueve al pool activo
                next_conn, next_addr = waiting_queue.get()
                connected_clients += 1  # añadiendo un nuevo cliente
                print(f"Procesando conexión en espera de {next_addr}")
                print(f"Clientes conectados actualmente: {connected_clients}/{max_players}")
                
                # crear y empezar un hilo por cliente
                client_thread = threading.Thread(target=handle_client, args=(next_conn, next_addr))
                client_thread.start()
                threads.append(client_thread)  # guardar hilo en colección
        time.sleep(1)  # espera de un segundo

def prompt_max_players():
    """Función para obtener max_players desde la entrada del usuario en un hilo separado."""
    global max_players
    max_players = int(input("Ingrese el maximo de clientes."))
    print(f"Máximo de jugadores establecido en {max_players}. Procesando conexiones en espera...")

def pool_manager():
    global connected_clients

    # Inicia un hilo que espera el valor de max_players
    threading.Thread(target=prompt_max_players, daemon=True).start()

    # Inicia un hilo que procesa continuamente la cola de espera
    threading.Thread(target=process_waiting_queue, daemon=True).start()

    # Configuración del socket del servidor
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
        TCPServerSocket.bind((HOST, PORT))
        TCPServerSocket.listen()
        print("(Server ON): ")

        while True:
            connection, address = TCPServerSocket.accept()
            
            with lock:
                if max_players is None:
                    print(f"Colocando a {address} en la cola de espera. Ingrese el numero max. de clientes.")
                    connection.sendall("En espera de configuración del servidor. Usted está en la cola.".encode('utf-8'))
                    waiting_queue.put((connection, address))
                elif connected_clients >= max_players:
                    print(f"El servidor está lleno. Colocando a {address} en la cola de espera.")
                    connection.sendall("En espera. Conexión en cola.".encode('utf-8'))
                    waiting_queue.put((connection, address))
                else:
                    connected_clients += 1
                    print(f"Nuevo cliente, conectados: {connected_clients}/{max_players}")
                    
                    # crear y empezar un hilo para manejar el cliente
                    client_thread = threading.Thread(target=handle_client, args=(connection, address))
                    client_thread.start()
                    threads.append(client_thread)  # guardar el hilo en la colección

if __name__ == "__main__":
    pool_manager()
