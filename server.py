import KBHit_py
import protocol
import select
from socket import socket, AF_INET, SOCK_STREAM

SERVER_PORT = 5555
SERVER_IP = '0.0.0.0'

client_sockets = []
messages_to_send = []
muted = []
socket_username = {}
managers = ['yuval']

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

def add_name(current_socket, name):    
    if name not in socket_username:
        socket_username[name] = current_socket
        return True
    if socket_username[name] is not current_socket:
        return False
    return True

def handle_message(current_socket, params):
    if not add_name(current_socket,params["name"]):
        name_exist(current_socket, params)
    elif params["command"] == 1:
        regular_messsage(current_socket, params)
    elif params["command"] == 2:
        add_manager(current_socket,params)
    elif params["command"] == 3:
        kick(current_socket,params)


def name_exist(current_socket, params):
    print(", user used a name that already exist.")
    params["data"] = "already exist! disconnecting you!"
    message = protocol.create_server_msg(params, 0, 400)
    messages_to_send.append((current_socket, message, True))

def regular_messsage(current_socket, params):
    if params["name"] in managers:
        params["name"] = '@' + params["name"]

    if params['data'] == 'quit':
        print(f", client {params["name"]} asked to quit.\nConnection was closed with {current_socket.getpeername()}")
        
        params["data"] = f"{params["name"]} has left the chat!"
        message = protocol.create_server_msg(params, 3)
        messages_to_send.extend(add_message(client_sockets, current_socket, message))
        
        client_sockets.remove(current_socket)
        if params['name'].startswith("@"):
            socket_username.pop(params['name'][1:])
        else:
            socket_username.pop(params['name'])
        current_socket.close()
    
    elif current_socket in muted:
        message = protocol.create_server_msg(params, 4, 403)
    else:
        print(f", client {params['name']} sent: {params['data']}")
        message = protocol.create_server_msg(params, 1)
        messages_to_send.extend(add_message(client_sockets, current_socket, message))

def kick(current_socket,params):
    try:
        if params["name"] in managers:
            kicked_socket = socket_username[params['data']]
            socket_username.pop(params['data'])

            params["data"] = f"{params["data"]} has been kicked out from the chat!"
            message = protocol.create_server_msg(params, 2)
            messages_to_send.extend(add_message(client_sockets, kicked_socket, message))
            
            params["data"] = f"You have been kicked out from the chat by @{params["name"]}!"
            message = protocol.create_server_msg(params, 2, 401)
            messages_to_send.append((kicked_socket, message, True))

            print(f", manager {params["name"]} kicked out {params["data"]}")
        else:
            params["data"] = f"You can't kick out other users, you are not a manager."
            message = protocol.create_server_msg(params, 2, 404)
            messages_to_send.append((current_socket, message))
    except KeyError:
        params["data"] = f"'{params["data"]}' can't be kicked out from the chat!"
        message = protocol.create_server_msg(params, 2, 405)
        messages_to_send.append((current_socket, message))

def add_manager(current_socket, params):
    if params["name"] in managers:
        managers.append(params["data"])
        params["data"] = f"{params["data"]} is now manager"

        message = protocol.create_server_msg(params, 2)
        messages_to_send.extend(add_message(client_sockets, current_socket, message))
    else:
        params["data"] = f"You can't add new manager, you are not a manager."
        message = protocol.create_server_msg(params, 2, 404)
        messages_to_send.append((current_socket, message))


def main():
    try:

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
                        if "closed" in params:
                            print(f", {params["closed"]}")
                            client_sockets.remove(current_socket)
                            current_socket.close()
                        else:
                            print(f", {params["error"]}")
                        continue

                    handle_message(current_socket, params)

            for message in messages_to_send:
                ok = False
                if len(message) == 3:
                    current_socket, data, ok= message
                else:
                    current_socket, data = message
                
                if current_socket in ready_wr:
                    print(f"Sending {current_socket.getpeername()}: {data.decode()[protocol.SERVER_FIELD_SIZE+protocol.STATUS_SIZE:]}")
                    current_socket.send(data)
                    messages_to_send.remove(message)

                if ok:
                    client_sockets.remove(current_socket)
                    current_socket.close()
            
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()