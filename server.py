import socket
import threading

# create a TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket to a specific address and port
server_address = ('localhost', 3000)
server_socket.bind(server_address)

# listen for incoming connections
server_socket.listen(5)

# list of connected clients
clients = []

def handle_client(client_socket, client_address):
    global clients

    # receive the client's registration message
    message = client_socket.recv(1024).decode()
    name, ip, port = message.split(',')

    # check if the client is already registered
    for client in clients:
        if client['name'] == name and client['ip'] == ip:
            response = 'User already registered'
            client_socket.send(response.encode())
            return

    # register the new client
    client = {'name': name, 'ip': ip, 'port': port, 'socket': client_socket}
    clients.append(client)

    # print a confirmation message
    print(f"New client registered: {name} ({ip}:{port})")

    # send a confirmation message to the client
    response = 'Registration successful'
    client_socket.send(response.encode())

    # handle incoming messages from the client
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message == 'list':
                response = get_client_list()
            elif message.startswith('details'):
                user = message.split(',')[1]
                # search for the client in the list
                for client in clients:
                    if client['name'] == user:
                        response = f"{client['ip']},{client['port']}"
            elif message == 'quit':
                client_socket.close()
                clients.remove(client)
                print(f"Client disconnected: {name} ({ip}:{port})")
                break
            else:
                response = f"{name}: {message}"
            client_socket.send(response.encode())
        except:
            client_socket.close()
            clients.remove(client)
            print(f"Client disconnected: {name} ({ip}:{port})")
            break

# get a list of connected clients
def get_client_list():
    global clients

    client_list = [client['name'] for client in clients]
    response = ','.join(client_list)
    return response

# accept incoming connections
while True:
    client_socket, client_address = server_socket.accept()
    print(f"New connection from {client_address[0]}:{client_address[1]}")
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()