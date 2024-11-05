#!/usr/bin/env python3
import socket
import time

HOST = "127.0.0.1"
PORT = 65432
BUFFER_SIZE = 1024

def connect_to_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientSocket:
        try:
            TCPClientSocket.connect((HOST, PORT))
            while True:
                # Recibir el mensaje de estado inicial del servidor
                initial_message = TCPClientSocket.recv(BUFFER_SIZE).decode('utf-8')
                print(initial_message)
                
                if "En espera" in initial_message:
                    print("Actualmente en la cola de espera. Esperando un espacio disponible...")
                    time.sleep(5)  # Espera de 5 segundos antes de verificar nuevamente
                    # No cerramos el socket, simplemente seguimos esperando
                    continue
                elif "Conectado" in initial_message:
                    # El cliente ahora está en el pool activo y puede empezar a interactuar
                    while True:
                        mensaje = input("escribe: ")
                        TCPClientSocket.sendall(mensaje.encode('utf-8'))

                        if mensaje.lower() == "adios":
                            print("cerrando conexion, adios")
                            return  # Sale de la función y finaliza la conexión

                        data = TCPClientSocket.recv(BUFFER_SIZE)
                        print("Respuesta del servidor:", repr(data.decode('utf-8')))
        except ConnectionRefusedError:
            print("No se pudo conectar al servidor, intenta nuevamente más tarde.")
        except BrokenPipeError:
            print("El servidor cerró la conexión inesperadamente.")

if __name__ == "__main__":
    connect_to_server()
