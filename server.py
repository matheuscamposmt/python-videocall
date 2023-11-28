import socket
import threading

# Define a classe ChatServer
class ChatServer:
    # Inicializa o servidor com o endereço padrão ('localhost', 3001)
    def __init__(self, server_address=('25.67.66.166', 3001)):
        # Cria um socket para o servidor
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Vincula o socket do servidor ao endereço especificado
        self.server_socket.bind(server_address)
        # Começa a ouvir conexões de clientes
        self.server_socket.listen(5)
        # Inicializa uma lista vazia para armazenar informações do cliente
        self.clients = []

    # Define um método para lidar com conexões de clientes
    def handle_client(self, client_socket, client_address):
        # Recebe uma mensagem do cliente
        message = client_socket.recv(1024).decode()
        # Divide a mensagem em nome, ip, porta e call_port
        name, ip, port, call_port = message.split(',')
        # Obtém o IP e a porta do socket do servidor
        server_socket_ip, server_socket_port = self.server_socket.getsockname()

        # Itera sobre os clientes existentes
        for client in self.clients:
            # Se um cliente com o mesmo nome e IP já existir, envia uma mensagem de erro
            if client['name'] == name and client['ip'] == ip:
                self.send_error(client_socket, 'Usuário já registrado')
                return
            # Se um cliente com o mesmo IP e call_port já existir, envia uma mensagem de erro
            elif client['ip'] == ip and client['call_port'] == call_port:
                self.send_error(client_socket, f'Falha ao registrar cliente: {name} - Já existe um usuário com esse IP recebendo chamadas nessa porta')
                return
        # Imprime uma mensagem indicando que um novo cliente está sendo registrado
        print(f"Registrando novo cliente: {name} ({ip}:{port} recebendo em {call_port}) no servidor {server_socket_ip}:{server_socket_port}")
        # Se o IP e call_port do cliente forem os mesmos do servidor, envia uma mensagem de erro
        if ip == server_socket_ip and call_port == str(server_socket_port):
            self.send_error(client_socket, f'Falha ao registrar cliente: {name} - Não é possível registrar essa porta porque é a porta do servidor')
            return
        
        # Se a call_port do cliente for a mesma que a sua porta, envia uma mensagem de erro
        if call_port == port:
            self.send_error(client_socket, f'Falha ao registrar cliente: {name} - A porta de chamada deve ser diferente da porta de conexão ao servidor')
            return

        # Cria um dicionário para armazenar as informações do cliente
        client = {'name': name, 'ip': ip, 'port': port, 'call_port': call_port, 'socket': client_socket}
        # Adiciona o cliente à lista de clientes
        
        # Imprime uma mensagem indicando que o cliente foi registrado
        print(f"Novo cliente registrado: {name} ({ip}:{port})")
        # Envia uma mensagem de sucesso para o cliente
        self.send_message(client_socket, 'success,Registrado com sucesso')

        # Conecta ao socket de chamada do cliente
        call_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        call_socket.connect((ip, int(call_port)))
        client['call_socket'] = call_socket

        self.clients.append(client)

        # Loop para lidar com as mensagens do cliente
        while True:
            try:
                # Recebe uma mensagem do cliente
                message = client_socket.recv(1024).decode()
                # Se a mensagem for 'list', obtém a lista de clientes
                if message == 'list':
                    response = self.get_client_list(client_socket)
                # Se a mensagem começar com 'details', obtém os detalhes do usuário especificado
                elif message.startswith('details'):
                    user = message.split(',')[1]
                    response = self.get_client_details(user)
                elif message.startswith('call_request'):
                    print(f"Usuário {name} solicitou uma chamada com {message.split(',')[1]}") 
                    call_recipient_ip = message.split(',')[1]
                    call_recipient_port = message.split(',')[2]
                    recipient = [client for client in self.clients if client['ip'] == call_recipient_ip and client['call_port'] == call_recipient_port][0]
                    callee_socket = recipient['call_socket']
                    self.send_call_request(call_socket, callee_socket, client)
                    response = ''
                # Se a mensagem for 'quit', desconecta o cliente
                elif message == 'quit':
                    self.disconnect_client(client_socket, client)
                    break
                # Caso contrário, a resposta é a mensagem do cliente
                else:
                    response = f"{name}: {message}"
                # Envia a resposta para o cliente
                self.send_message(client_socket, response)
            # Se ocorrer um erro, desconecta o cliente
            except:
                self.disconnect_client(client_socket, client)
                break

    def send_call_request(self, caller_socket, callee_socket, client):
        callee_socket.send(f"{client['name']},{client['ip']},{client['call_port']}".encode())
        print(f"Enviando solicitação de chamada para {callee_socket.getpeername()[0]}:{callee_socket.getpeername()[1]}")
        response = callee_socket.recv(1024).decode()
        if response.startswith('accept'):
            caller_socket.send(response.encode())
        else:
            caller_socket.send(response.encode())

    # Define um método para enviar uma mensagem de erro
    def send_error(self, client_socket, error_message):
        response = f'error,{error_message}'
        # Imprime a mensagem de erro
        print(response.split(',')[1])
        # Envia a mensagem de erro para o cliente
        self.send_message(client_socket, response)

    # Define um método para enviar uma mensagem
    def send_message(self, client_socket, message):
        # Envia a mensagem para o cliente
        client_socket.send(message.encode())

    # Define um método para obter a lista de clientes
    def get_client_list(self, client_socket):
        # Cria uma lista com os nomes dos clientes
        client_list = [client['name'] for client in self.clients if client['socket'] != client_socket]
        # Retorna a lista de clientes como uma string
        return ','.join(client_list) if client_list else 'not_found'
    
    # Define um método para obter os detalhes do cliente
    def get_client_details(self, user):
        # Itera sobre os clientes
        for client in self.clients:
            # Se o nome do cliente corresponder ao usuário especificado, retorna o IP e a porta de chamada do cliente
            if client['name'] == user:
                return f"{client['ip']},{client['call_port']}"

    # Define um método para desconectar um cliente
    def disconnect_client(self, client_socket, client):
        # Envia uma mensagem para o cliente informando que a conexão foi encerrada
        client_socket.send('Conexão encerrada'.encode())
        # Fecha o socket do cliente
        client_socket.close()
        # Se o cliente estiver na lista de clientes, remove-o
        if client in self.clients:
            self.clients.remove(client)
        # Imprime uma mensagem indicando que o cliente foi desconectado
        print(f"Cliente desconectado: {client['name']} ({client['ip']}:{client['port']})")

    # Define um método para executar o servidor
    def run(self):
        # Imprime uma mensagem indicando que o servidor foi iniciado
        print(f"Servidor iniciado em {self.server_socket.getsockname()[0]}:{self.server_socket.getsockname()[1]}")
        # Loop para aceitar conexões de clientes
        while True:
            # Aceita uma conexão de cliente
            client_socket, client_address = self.server_socket.accept()
            # Imprime uma mensagem indicando que uma nova conexão foi estabelecida
            print(f"Nova conexão de {client_address[0]}:{client_address[1]}")
            # Cria uma nova thread para lidar com o cliente
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            # Inicia a thread
            client_thread.start()

# Se este script for o principal, cria um novo servidor e o executa
if __name__ == "__main__":
    server = ChatServer()
    server.run()