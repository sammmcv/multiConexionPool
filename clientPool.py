#!/usr/bin python3
import socket

HOST = "127.0.0.1"
PORT = 65432
buffer_size = 1024

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientSocket:
    TCPClientSocket.connect((HOST, PORT))
    print("conectado, escribe 'adios' para terminar:")
    
    while True:
        mensaje = input("escribe: ")
        TCPClientSocket.sendall(mensaje.encode('utf-8')) #envio

        if mensaje.lower() == "adios":
            print("cerrando conexion, ayos")
            break

        data = TCPClientSocket.recv(buffer_size) # mensajes del server
        print("recibiste:", repr(data), "de", TCPClientSocket.getpeername())

print("fin.")
