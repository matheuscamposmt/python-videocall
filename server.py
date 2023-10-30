import socket
import threading

class ChatServer:
    def __init__(self, server_address=('localhost', 3001)):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(server_address)
        self.server_socket.listen(5)
        self.clients = []

    def handle_client(self, client_socket, client_address):
        message = client_socket.recv(1024).decode()
        name, ip, port, call_port = message.split(',')
        server_socket_ip, server_socket_port = self.server_socket.getsockname()

        for client in self.clients:
            if client['name'] == name and client['ip'] == ip:
                self.send_error(client_socket, 'Usuário já registrado')
                return
            elif client['ip'] == ip and client['call_port'] == call_port:
                self.send_error(client_socket, f'Falha ao registrar cliente: {name} - Já existe um usuário com esse IP recebendo chamadas nessa porta')
                return
        print(f"Registrando novo cliente: {name} ({ip}:{port} recebendo em {call_port}) no servidor {server_socket_ip}:{server_socket_port}")
        if ip == server_socket_ip and call_port == str(server_socket_port):
            self.send_error(client_socket, f'Falha ao registrar cliente: {name} - Não é possível registrar essa porta porque é a porta do servidor')
            return
        
        if call_port == port:
            self.send_error(client_socket, f'Falha ao registrar cliente: {name} - A porta de chamada deve ser diferente da porta de conexão ao servidor')
            return

        client = {'name': name, 'ip': ip, 'port': port, 'call_port': call_port, 'socket': client_socket}
        self.clients.append(client)
        print(f"Novo cliente registrado: {name} ({ip}:{port})")
        self.send_message(client_socket, 'success,Registrado com sucesso')

        while True:
            try:
                message = client_socket.recv(1024).decode()
                if message == 'list':
                    response = self.get_client_list()
                elif message.startswith('details'):
                    user = message.split(',')[1]
                    response = self.get_client_details(user)
                elif message == 'quit':
                    self.disconnect_client(client_socket, client)
                    break
                else:
                    response = f"{name}: {message}"
                self.send_message(client_socket, response)
            except:
                self.disconnect_client(client_socket, client)
                break

    def send_error(self, client_socket, error_message):
        response = f'error,{error_message}'
        print(response.split(',')[1])
        self.send_message(client_socket, response)

    def send_message(self, client_socket, message):
        client_socket.send(message.encode())

    def get_client_list(self):
        client_list = [client['name'] for client in self.clients]
        return ','.join(client_list)

    def get_client_details(self, user):
        for client in self.clients:
            if client['name'] == user:
                return f"{client['ip']},{client['call_port']}"

    def disconnect_client(self, client_socket, client):
        client_socket.send('Conexão encerrada'.encode())
        client_socket.close()
        if client in self.clients:
            self.clients.remove(client)
        print(f"Cliente desconectado: {client['name']} ({client['ip']}:{client['port']})")


    def run(self):
        print(f"Servidor iniciado em {self.server_socket.getsockname()[0]}:{self.server_socket.getsockname()[1]}")
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Nova conexão de {client_address[0]}:{client_address[1]}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()

if __name__ == "__main__":
    server = ChatServer()
    server.run()