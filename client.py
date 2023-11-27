import socket

# Define a class for the ChatClient
class Client:
    def __init__(self, server_address):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(server_address)
        self.ip, self.port = self.client_socket.getsockname()
        self.registered = False

    def register(self, name, client_call_port):
        # Cria uma mensagem com o nome, IP, porta e porta de chamada do cliente
        message = ','.join([name, self.ip, str(self.port), str(client_call_port)])
        # Envia a mensagem para o servidor
        self.client_socket.send(message.encode())
        # Recebe uma resposta do servidor
        response = self.client_socket.recv(1024).decode().split(',')
        # Imprime a resposta
        print(response[1])
        # Se a resposta for um erro, fecha o socket do cliente e encerra o programa
        if response[0] == 'error':
            self.client_socket.close()
            exit()
        
        self.registered = True


    def get_user_list(self):
        self.send_message('list')
        response = self.client_socket.recv(1024).decode()
        if response == 'not_found':
            return
        user_list = response.split(',')
        
        return user_list

    def get_user_details(self, user):
        self.send_message(f'details,{user}')
        response = self.client_socket.recv(1024).decode()
        ip, port = response.split(',')

        data = dict(user=user, ip=ip, port=port)
        
        return data

    def quit(self):
        self.send_message('quit')
        response = self.client_socket.recv(1024).decode()
        print(response)
        self.client_socket.close()
        
        return response

    def send_message(self, message):
        self.client_socket.send(message.encode())