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

    
    def call_user(self, selected_user):
        # Cria uma mensagem com o nome, IP, porta e porta de chamada do cliente
        message = ','.join([user, user_ip, user_port, selected_user])
        # Envia a mensagem para o servidor
        self.send_message(message)
        # Recebe uma resposta do servidor
        response = self.client_socket.recv(1024).decode()
        # Imprime a resposta
        print(response)
        
    def start_video_call(self, invitee_port):
        self.target_ip = self.ip
        if invitee_port == '4500':
            self.streaming_server_port = 4000
        else:
            self.streaming_server_port = 4500
        self.target_port = int(invitee_port)
        self.stream_server = StreamingServer(self.target_ip, self.streaming_server_port)
        self.camera_client = CameraClient(self.target_ip, self.target_port)
        self.stream_server.start_server()
        time.sleep(2)
        self.camera_client.start_stream()

    def answer_call(self, caller, caller_ip, caller_port, call_port):
        # Cria uma mensagem com o nome, IP, porta e porta de chamada do cliente
        message = ','.join([caller, caller_ip, caller_port, str(call_port), 'yes'])
        # Envia a mensagem para o servidor
        self.send_message(message)
        # Recebe uma resposta do servidor
        response = self.client_socket.recv(1024).decode()
        # Imprime a resposta
        print(response)
        # Se a resposta for um erro, fecha o socket do cliente e encerra o programa
        if response == 'error':
            self.client_socket.close()
            exit()
        self.start_video_call(caller_port)



    def receive_call(self):
        while True:
            # listen for incoming messages from the server
            message = self.client_socket.recv(1024).decode()
            # if the message starts with 'call', get the caller's details
            if message.startswith('call'):
                caller = message.split(',')[1]
                caller_ip = message.split(',')[2]
                caller_port = message.split(',')[3]
                # if the caller's details are valid, answer the call
                if caller_ip and caller_port:
                    self.answer_call(caller, caller_ip, caller_port, self.port)
                    break