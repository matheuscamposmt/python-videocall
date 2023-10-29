import socket
import threading

# cria um socket TCP/IP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# define o endereço e porta do servidor
server_address = ('localhost', 3000)
server_socket.bind(server_address)

# inicia o servidor
server_socket.listen(5)

# lista de clientes conectados
clients = []

def handle_client(client_socket, client_address):
    global clients

    # recebe uma mensagem de registro do cliente
    message = client_socket.recv(1024).decode()
    name, ip, port, call_port = message.split(',')

    # checa se o cliente já está registrado
    for client in clients:
        if client['name'] == name and client['ip'] == ip:
            response = 'error,Usuário já registrado'
            print(response.split(',')[1])
            client_socket.send(response.encode())
            return
        elif client['ip'] == ip and client['call_port'] == call_port:
            response = f"error,Falha ao registrar cliente: {name} - Já existe um usuário com esse IP recebendo chamadas nessa porta"
            print(response.split(',')[1])
            client_socket.send(response.encode())
            return

    # verifica se a porta de chamada é diferente da porta de conexão ao servidor
    if call_port == port:
        response = f"error,Falha ao registrar cliente: {name} - A porta de chamada deve ser diferente da porta de conexão ao servidor"
        print(response.split(',')[1])
        client_socket.send(response.encode())
        return
    
    client = {'name': name, 'ip': ip, 'port': port, 'call_port': call_port, 'socket': client_socket}
    clients.append(client)

    # imprime uma mensagem de registro
    print(f"Novo cliente registrado: {name} ({ip}:{port})")

    # envia uma mensagem de registro bem sucedido para o cliente
    response = 'success,Registrado com sucesso'
    client_socket.send(response.encode())

    # trata as mensagens recebidas do cliente
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message == 'list':
                response = get_client_list()
            elif message.startswith('details'):
                user = message.split(',')[1]
                for client in clients:
                    if client['name'] == user:
                        response = f"{client['ip']},{client['call_port']}"
            elif message == 'quit':
                client_socket.close()
                clients.remove(client)
                print(f"Cliente desconectado: {name} ({ip}:{port})")
                break
            else:
                response = f"{name}: {message}"
            client_socket.send(response.encode())
        except:
            client_socket.close()
            if client in clients:
                clients.remove(client)
            print(f"Cliente desconectado: {name} ({ip}:{port})")
            break

# retorna a lista de clientes conectados
def get_client_list():
    global clients

    client_list = [client['name'] for client in clients]
    response = ','.join(client_list)
    return response

# aguarda por novas conexões
while True:
    client_socket, client_address = server_socket.accept()
    print(f"Nova conexão de {client_address[0]}:{client_address[1]}")
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()