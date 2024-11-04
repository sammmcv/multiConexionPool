#!/usr/bin python3
import socket
import threading
from queue import Queue

HOST = "127.0.0.1"
PORT = 65432
buffer_size = 1024
MAX_CONNECTIONS = 5

connection_pool = Queue(maxsize=MAX_CONNECTIONS)

connected_clients = 0 #contador
# para evitar problemas de concurrencia con el contador
lock = threading.Lock()

def handle_client(connection, address):
    global connected_clients
    print(f"conectado al clente con ip: {address}")
    
    try:
        while True:
            data = connection.recv(buffer_size)
            if not data:
                print(f"{address} ha cerrado la conexión.")
                break
            print(f"mensaje: {data} de {address}")
            connection.sendall(data)
    except ConnectionResetError:
        print(f"{address} se desconectó inesperadamente.")
    except ConnectionAbortedError:  # nueva excepción añadida
        print(f"{address} ha abortado la conexión localmente.")
    finally:
        connection.close()
        with lock:
            connected_clients -= 1
            print(f"clientes conectados actualmente: {connected_clients}")

def pool_manager(): #pool
    global connected_clients
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
        TCPServerSocket.bind((HOST, PORT))
        TCPServerSocket.listen()
        print("el server esta disponible y en espera de solicitudes")

        while True:
            connection, address = TCPServerSocket.accept()
            print(f"conexion aceptada de {address}")

            # standby mientras se hace un espacio
            if connection_pool.full():
                print("el pool esta lleno, esperando...")
            
            # nueva conexion al pool
            connection_pool.put(connection)

            with lock:
                connected_clients += 1
                print(f"nuevo cliente, conectados: {connected_clients}")

            # thread que gestiona la conexion
            client_thread = threading.Thread(target=handle_client, args=(connection, address))
            client_thread.start()

            # para cuando se termina la conexion, se quita del pool
            connection_pool.get()

if __name__ == "__main__":
    pool_manager()
