import datetime

NAME_LENGTH_FIELD_SIZE = 1
LENGTH_FIELD_SIZE = 2
SERVER_FIELD_SIZE = 2
STATUS_SIZE = 3

def create_client_msg(data, name, command, receiver):
    
    name_length = str(len(name))
    zfill_name_length = name_length.zfill(NAME_LENGTH_FIELD_SIZE)
    
    length = str(len(data))
    zfill_length = length.zfill(LENGTH_FIELD_SIZE)

    if command == 5:
        receiver_len = str(len(receiver))
        zfill_receiver_len = receiver_len.zfill(NAME_LENGTH_FIELD_SIZE)
        message = f"{zfill_name_length}{name}{command}{zfill_receiver_len}{receiver}{zfill_length}{data}"
        return message.encode()
        
    message = f"{zfill_name_length}{name}{command}{zfill_length}{data}"

    return message.encode()

def get_client_msg(my_socket):
    msg_values = {}
    try:
        time = datetime.datetime.now()
        msg_values["time"] = f"{time:%H:%M}"

        name_length = my_socket.recv(NAME_LENGTH_FIELD_SIZE).decode()
        if name_length == '':
            msg_values['closed'] = "disconnected for some reasons"
            return False, msg_values
        name_length = int(name_length)
        
        name = my_socket.recv(name_length).decode()
        msg_values["name"] = name

        command = int(my_socket.recv(1).decode())
        msg_values["command"] = command

        if command == 5:
            receiver_length = my_socket.recv(NAME_LENGTH_FIELD_SIZE).decode()
            if receiver_length == '':
                return False, {'error': "Error receiving massage."}        
            receiver_length = int(receiver_length)

            receiver = my_socket.recv(receiver_length).decode()
            msg_values["receiver"] = receiver

        data_length = my_socket.recv(LENGTH_FIELD_SIZE).decode()
        if data_length == '':
            return False, {'error': "Error receiving massage."}
        data_length = int(data_length)

        data = my_socket.recv(data_length).decode()
        msg_values["data"] = data

        return True, msg_values
    except ValueError:
        junk =  my_socket.recv(1024).decode()
        return False, {'error': "Error receiving massage."}

def get_server_msg(my_socket):
    try:
        status = int(my_socket.recv(STATUS_SIZE))
        data_length = my_socket.recv(SERVER_FIELD_SIZE).decode()
        if data_length == '':
            return False, 500, ''
        data_length = int(data_length)

        data = my_socket.recv(data_length).decode()
        return True, status, data

    except ValueError:
        return False, 500, "Error receiving massage"
    
def create_server_msg(message_params,format, status = 200):
    message = ''
    if format == 0:
        message = f"{message_params["time"]} name {message_params["name"]} {message_params["data"]}"
    if format == 1: 
        message = f"{message_params["time"]} {message_params["name"]}: {message_params["data"]}"
    if format == 2:
        message = f"{message_params["time"]} {message_params["data"]}"
    message_len = str(len(message))
    message_len_fill = message_len.zfill(SERVER_FIELD_SIZE)

    full_message = str(status) + message_len_fill + message

    return full_message.encode()

def main():
    pass

if __name__ == "__main__":
    main()