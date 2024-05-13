
def create_msg(data, ):
    length = str(len(data))
    zfill_length = length.zfill(LENGTH_FIELD_SIZE)
    message = zfill_length + data
    return message.encode()

def get_msg(my_socket):
    try:
        message_length = my_socket.recv(LENGTH_FIELD_SIZE).decode()
        if message_length == '':
            return False, ''
        message_length = int(message_length)
        data = my_socket.recv(message_length).decode()
        return True, data
    except ValueError:
        junk =  my_socket.recv(1024).decode()
        return False, "Error receiving massage"
    
def main():
    pass

if __name__ == "__main__":
    main()