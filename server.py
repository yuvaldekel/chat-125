import KBHit_py
import protocol
import select
from socket import socket, AF_INET, SOCK_STREAM

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
        client_sockets = []
        messages_to_send = []
        socket_username = {}
        managers = ['yuval']

        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen()
        
        while True:

            ready_rd , ready_wr , in_error = select.select([server_socket] + client_sockets, client_sockets, [])
            
            for current_socket in ready_rd:
                
                if current_socket is server_socket:
                    (connection_socket, address) = current_socket.accept()
                    print(f"New client {address}.")
                    client_sockets.append(connection_socket)
                    print_client_sockets(client_sockets)
                else:
                    print(f"Getting data from existing client {current_socket.getpeername()}", end='')
                    ok, params = protocol.get_client_msg(current_socket)

                    if not ok:
                        print(f" {params["error"]}")
                        continue

                    socket_username[params['name']] = current_socket

                    if params['data'] == 'quit':
                        print(f", client asked to quit.\nConnection was closed with {current_socket.getpeername()}")
                        
                        params["data"] = "has left the chat!"
                        message = protocol.create_server_msg(params)
                        messages_to_send.extend(add_message(client_sockets, current_socket, message))
                    
                        client_sockets.remove(current_socket)
                        socket_username.pop(params['name'])
                        current_socket.close()
                    else:
                        print(f", client {params['name']} sent: {params['data']}")
                        message = protocol.create_server_msg(params)
                        messages_to_send.extend(add_message(client_sockets, current_socket, message))

            for message in messages_to_send:
                current_socket, data = message
                
                if current_socket in ready_wr:
                    print(f"Sending {current_socket.getpeername()}: {data.decode()[protocol.SERVER_FIELD_SIZE:]}")
                    current_socket.send(data)
                    messages_to_send.remove(message)
            
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()