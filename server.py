import protocol # type: ignore
import select
from socket import socket, AF_INET, SOCK_STREAM

SERVER_PORT = 8881
SERVER_IP = '0.0.0.0'

client_sockets : list[socket] = []
messages_to_send = []
muted : list[str] = []
socket_username : dict[str:socket] = {}
hard_coded_managers : list[str] = ["yuval"]
managers : list[str] = ['yuval']

def print_client_sockets(client_sockets):
    length = len(client_sockets)
    print("Printing list of connected clients")
    
    print("[", end='')
    
    for i,c in enumerate(client_sockets):
        print(f"{c.getpeername()}",end='')
        if i+1 != length:
            print(", ",end='')
    
    print("]")

def add_message(client_sockets , sending_socket, data, exit = False):
    message_list = []
    for current_socket in client_sockets:
        if not current_socket is sending_socket:
            message_list.append((current_socket, data , exit))
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
    elif params["command"] == 4:
        mute(current_socket,params)
    elif params["command"] == 5:
        private(current_socket,params)

def name_exist(current_socket, params):
    print(", user used a name that already exist.")
    params["data"] = "already exist! disconnecting you!"
    message = protocol.create_server_msg(params, 0, 400)
    messages_to_send.append((current_socket, message, True))

def regular_messsage(current_socket, params):
    name = params["name"]

    if params['data'] == 'quit':
        print(f", client {params["name"]} asked to quit. Connection was closed with {current_socket.getpeername()}")

        params["data"] = f"{params["name"]} has left the chat!"
        message = protocol.create_server_msg(params, 2)
        messages_to_send.extend(add_message(client_sockets, current_socket, message))
        
        if current_socket in muted:
            muted.remove(current_socket)
        if name not in hard_coded_managers and name in managers:
            managers.remove(name)
        
        client_sockets.remove(current_socket)
        socket_username.pop(name)
        current_socket.close()

    elif params['data'] == "view-managers":
        print(f", client {name} asked to view the managers list.")
    
        params["data"] = f"{managers}"
        message = protocol.create_server_msg(params, 2)
        messages_to_send.append((current_socket, message, False))  
    
    elif current_socket in muted:
        print(f", client {name} cannot speak.")
    
        params["data"] = "You cannot speak here."
        message = protocol.create_server_msg(params, 2, 402)
        messages_to_send.append((current_socket, message, False))
    else:
        if name in managers:
            params["name"] = '@' + name
        
        print(f", client {params['name']} sent: {params['data']}")
        message = protocol.create_server_msg(params, 1)
        messages_to_send.extend(add_message(client_sockets, current_socket, message))

def kick(current_socket,params):
    try:
        if params["name"] in managers:
            to_kick = params['data']
            kicked_socket = socket_username[to_kick]

            params["data"] = f"{to_kick} has been kicked out from the chat!"
            message = protocol.create_server_msg(params, 2)
            messages_to_send.extend(add_message(client_sockets, kicked_socket, message))
            
            params["data"] = f"You have been kicked out from the chat by @{params["name"]}!"
            message = protocol.create_server_msg(params, 2, 401)
            messages_to_send.append((kicked_socket, message, True))

            if to_kick in managers and to_kick not in hard_coded_managers:
                managers.remove(to_kick)
            if kicked_socket in muted:
                muted.remove(kicked_socket)
            socket_username.pop(to_kick)

            print(f", manager @{params["name"]} kicked out {to_kick}")
        else:
            params["data"] = f"You can't kick out other users, you are not a manager."
            message = protocol.create_server_msg(params, 2, 403)
            messages_to_send.append((current_socket, message, False))
    except KeyError:
        params["data"] = f"'{params["data"]}' can't be kicked out from the chat!, he is not a member of this chat."
        message = protocol.create_server_msg(params, 2, 404)
        messages_to_send.append((current_socket, message, False))

def add_manager(current_socket, params):
    to_manager = params['data']
    if params["name"] in managers:
        if to_manager not in socket_username:
            print(f", {params["name"]} asked to add new manager, but {to_manager} does not exist.")
            params["data"] = f"You can't make {to_manager} manager, he is not a member of this chat."
            message = protocol.create_server_msg(params, 2, 404)
            messages_to_send.append((current_socket, message, False))
        elif to_manager in managers:
            print(f", {params["name"]} asked to add new manager, but {to_manager} is already a manager.")
            params["data"] = f"You can't make {to_manager} manger, he is already manager."
            message = protocol.create_server_msg(params, 2, 405)
            messages_to_send.append((current_socket, message, False))
        else:
            print(f", {params["name"]} added a new manager {to_manager}.")
            managers.append(to_manager)
            params["data"] = f"{to_manager} is now manager"

            message = protocol.create_server_msg(params, 2)
            messages_to_send.extend(add_message(client_sockets, current_socket, message))
            messages_to_send.append((current_socket, message, False))

    else:
        print(f", {params["name"]} asked to add a new manager, but he cannot.")
        params["data"] = f"You can't add new manager, you are not a manager."
        message = protocol.create_server_msg(params, 2, 403)
        messages_to_send.append((current_socket, message, False))

def mute(current_socket, params):

    to_mute = params['data']
    if params["name"] in managers:
        if to_mute not in socket_username:
            print(f", {params["name"]} asked to mute a member, but {to_mute} does not exist.")
            params["data"] = f"You can't mute {to_mute}, he is not a member of this chat."
            message = protocol.create_server_msg(params, 2, 404)
            messages_to_send.append((current_socket, message, False))
        elif socket_username[to_mute] in muted:
            print(f", {params["name"]} asked to mute a member, but {to_mute} is already a manager.")
            params["data"] = f"You can't mute {to_mute}, he is already muted."
            message = protocol.create_server_msg(params, 2, 405)
            messages_to_send.append((current_socket, message, False))
        else:
            print(f", {params["name"]} muted {to_mute}.")
            muted.append(socket_username[to_mute])
            params["data"] = f"You muted {to_mute}."
            message = protocol.create_server_msg(params, 2)
            messages_to_send.append((current_socket, message, False))
    else:
        print(f", {params["name"]} asked to add a mute someone, but he cannot.")
        params["data"] = f"You can't mute other members, you are not a manager."
        message = protocol.create_server_msg(params, 2, 403)
        messages_to_send.append((current_socket, message,False))
    
def private(current_socket,params):
    receiver = params["receiver"]
    if receiver in socket_username:
        receiver_socket = socket_username[receiver]
        print(f", client {params['name']} wanted to send a privte message {params['data']} to {receiver}")
        message = protocol.create_server_msg(params, 1)
        messages_to_send.append((receiver_socket, message, False))
    else:
        print(f", client {params['name']} sent: privte message {params['data']} to a client that does not exist")
        params["data"] = f"{receiver} is not a member of this chat, you cannot send him a message."
        message = protocol.create_server_msg(params, 2)
        messages_to_send.append((current_socket, message, False))

def closed(current_socket, params):
    print(f", {params["closed"]}")
    try:  
        users = list(socket_username.keys())
        sockets = list(socket_username.values())
        closed_name = users[sockets.index(current_socket)]

        params["data"] = f"{closed_name} {params["closed"]}"
        message = protocol.create_server_msg(params, 2)
        messages_to_send.extend(add_message(client_sockets, current_socket, message))

        if closed_name in managers and closed_name not in hard_coded_managers:
            managers.remove(closed_name)
        if current_socket in muted:
            muted.remove(current_socket)
        socket_username.pop(closed_name)

    except ValueError:
        pass
    finally:
        client_sockets.remove(current_socket)
        current_socket.close()

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
                            closed(current_socket, params)
                        else:
                            print(f", {params["error"]}")
                        continue

                    handle_message(current_socket, params)

            for message in messages_to_send:
                
                current_socket, data, exit= message
                
                if current_socket in ready_wr:
                    print(f"Sending {current_socket.getpeername()}: {data.decode()[protocol.SERVER_FIELD_SIZE+protocol.STATUS_SIZE:]}")
                    current_socket.send(data)
                    messages_to_send.remove(message)

                if exit:
                    client_sockets.remove(current_socket)
                    current_socket.close()
            
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()