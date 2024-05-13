import select
from socket import socket, AF_INET, SOCK_STREAM

MAX_SIZE = 1024
SERVER_PORT = 5555
SERVER_IP = '0.0.0.0'

def print_client_sockets(client_sockets):
    length = len(client_sockets)
    print("Printing list of connected clients")
    
    print("[", end='')
    
    for i,c in enumerate(client_sockets):
        print(f"{c.getpeername()}",end='')
        if i+1 != length:
            print(", ",end='')
    
    print("]")

def add_message(client_sockets , sending_socket, data):
    message_list = []
    for current_socket in client_sockets:
        if not current_socket is sending_socket:
            message_list.append((current_socket, data))
    return message_list

def main():
    try:
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen()
        client_sockets = []
        socket_to_send = []
        
        while True:
            rd_list = [server_socket] + client_sockets
            ready_rd , ready_wr , in_error = select.select(rd_list, client_sockets, [])
            
            for current_socket in ready_rd:
                
                if current_socket is server_socket:
                    (connection_socket, address) = current_socket.accept()
                    print(f"Hello new client {address}.")
                    client_sockets.append(connection_socket)
                    print_client_sockets(client_sockets)
                else:
                    print(f"Getting data from existing client {current_socket.getpeername()}", end='')
                    data = current_socket.recv(MAX_SIZE).decode()

                    if data == '':
                        print(", client did not sent anyting.")
                        print(f"Connection was closed with {current_socket.getpeername()}")
                        client_sockets.remove(current_socket)
                        current_socket.close()
                    else:
                        print(f", client sent: {data}")
                        socket_to_send.extend(add_message(client_sockets, current_socket, data))

            for message in socket_to_send:
                current_socket, data = message
                
                if current_socket in ready_wr:
                    print(f"Sending {current_socket.getpeername()}: {data}")
                    current_socket.send(data.encode())
                    socket_to_send.remove(message)

    finally:
        server_socket.close()

if __name__ == "__main__":
    main()