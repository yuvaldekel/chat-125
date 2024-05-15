import datetime

NAME_LENGTH_FIELD_SIZE = 1
LENGTH_FIELD_SIZE = 2
SERVER_FIELD_SIZE = 2


def create_client_msg(data, name, command = 1):
    naem_length = str(len(name))
    zfill_nzme_length = naem_length.zfill(NAME_LENGTH_FIELD_SIZE)
    
    length = str(len(data))
    zfill_length = length.zfill(LENGTH_FIELD_SIZE)
    
    message = f"{zfill_nzme_length}{name}{command}{zfill_length}{data}"
    return message.encode()

def get_client_msg(my_socket):
    msg_values = {}
    try:
        
        name_length = my_socket.recv(NAME_LENGTH_FIELD_SIZE).decode()
        if name_length == '':
            return False, {}
        name_length = int(name_length)
        
        name = my_socket.recv(name_length).decode()
        msg_values["name"] = name

        command = int(my_socket.recv(1).decode())
        msg_values["command"] = command

        data_length = my_socket.recv(LENGTH_FIELD_SIZE).decode()
        if data_length == '':
            return False, {}
        data_length = int(data_length)

        data = my_socket.recv(data_length).decode()
        msg_values["data"] = data

        time = datetime.datetime.now()
        msg_values["time"] = f"{time:%H:%M}"

        return True, msg_values
    except ValueError:
        junk =  my_socket.recv(1024).decode()
        return False, {'error': "Error receiving massage."}

def get_server_msg(my_socket):
    try:
        data_length = my_socket.recv(SERVER_FIELD_SIZE).decode()
        if data_length == '':
            return False, ''
        data_length = int(data_length)

        data = my_socket.recv(data_length).decode()
        return True, data

    except ValueError:
        return False, "Error receiving massage"
    
def create_server_msg(message_params):
    message = ''
    if message_params["command"] == 1: 
        message = f"{message_params["time"]} {message_params["name"]}: {message_params["data"]}"
    message_len = str(len(message))
    message_len_fill = message_len.zfill(SERVER_FIELD_SIZE)

    full_message = message_len_fill + message
    return full_message.encode()

def main():
    pass

if __name__ == "__main__":
    main()