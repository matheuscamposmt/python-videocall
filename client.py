import socket
import tkinter as tk
import threading
from vidstream import StreamingServer, CameraClient, AudioSender, AudioReceiver
import time

# Define a classe ChatClient
class ChatClient:
    # Inicializa o cliente com o endereço do servidor padrão ('localhost', 3001)
    def __init__(self, client_call_port, server_address=('25.67.66.166', 3001)):
        # Cria um socket para o cliente
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Conecta o socket do cliente ao endereço do servidor
        self.client_socket.connect(server_address)
        # Obtém o IP e a porta do socket do cliente
        self.ip, self.port = self.client_socket.getsockname()
        # Cria uma janela Tkinter para a interface do usuário
        self.root = tk.Tk()
        self.root.title('Chat Client')
        # Cria uma lista de usuários na interface do usuário
        self.user_list = tk.Listbox(self.root)
        self.user_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Vincula um evento de clique duplo na lista de usuários a um método de retorno de chamada
        self.user_list.bind('<Double-1>', self.callback)

        # Cria um botão para consultar a lista de usuários
        self.list_button = tk.Button(self.root, text='Consultar usuários', command=self.show_user_list)
        self.list_button.pack(side=tk.LEFT)

        # Cria um botão para encerrar a conexão
        self.quit_button = tk.Button(self.root, text='Encerrar conexão', command=lambda: self.send_message('quit', self.client_socket))
        self.quit_button.pack(side=tk.LEFT)

        self.call_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.call_socket.bind((self.ip, client_call_port))
        self.call_socket.listen(1)
        threading.Thread(target=self.listen_to_server).start()

    # Define um método para registrar o cliente no servidor
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

    # Define um método de retorno de chamada para o evento de clique duplo na lista de usuários
    def callback(self, event):
        # Obtém o índice do item selecionado na lista de usuários
        selection = event.widget.curselection()
        # Se um item foi selecionado, obtém os detalhes do usuário
        if selection:
            index = selection[0]
            data = event.widget.get(index)
            self.show_user_details(data)

    # Define um método para mostrar a lista de usuários
    def show_user_list(self):
        # Envia uma mensagem para o servidor solicitando a lista de usuários
        self.send_message('list', self.client_socket)
        # Recebe a lista de usuários do servidor
        response = self.client_socket.recv(1024).decode()
        # Se a resposta for 'not_found', não há usuários registrados no servidor sem ser o cliente atual
        if response == 'not_found':
            return
        # Limpa a lista de usuários na interface do usuário
        self.user_list.delete(0, tk.END)
        # Adiciona cada usuário à lista de usuários na interface do usuário
        for user in response.split(','):
            self.user_list.insert(tk.END, user)
        # Atualiza a interface do usuário
        self.root.update()

    # Define um método para mostrar os detalhes de um usuário
    def show_user_details(self, user):
        # Envia uma mensagem para o servidor solicitando os detalhes do usuário
        self.send_message(f'details,{user}', self.client_socket)
        # Recebe os detalhes do usuário do servidor
        response = self.client_socket.recv(1024).decode()
        # Divide a resposta em IP e porta
        ip, port = response.split(',')
        # Cria uma nova janela para mostrar os detalhes do usuário
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Detalhes de {user}")
        # Cria um rótulo para mostrar o IP e a porta do usuário
        detail_label = tk.Label(detail_window, text=f"IP: {ip}\nPorta: {port}")
        detail_label.pack(side=tk.TOP)
        # Cria um botão para ligar para o usuário
        call_button = tk.Button(detail_window, text='Ligar', command=lambda: self.call_request(ip, int(port)))
        call_button.pack(side=tk.TOP)

    # Define um método para enviar uma mensagem para o servidor
    def send_message(self, message, socket=None):
        # Envia a mensagem para o servidor
        socket.send(message.encode())
        # Se a mensagem for 'quit', recebe uma resposta do servidor, imprime a resposta, fecha o socket do cliente e encerra a interface do usuário
        if message == 'quit':
            response = socket.recv(1024).decode()
            print(response)
            socket.close()
            self.call_socket.close()
            self.root.destroy()
            self.root.quit()

    # Define um método para solicitar uma chamda ao servidor
    def call_request(self, ip, port):
        # Envia uma mensagem para o servidor solicitando uma chamada
        self.send_message(f"call_request,{ip},{port}", self.client_socket)
    
        print(self.client_socket.recv(1024).decode())
        
    def listen_to_server(self):
        while True:
            conn, addr = self.call_socket.accept()
            message = conn.recv(1024).decode()
            print(message)
            if not message.startswith('accept'):
                call_window = tk.Tk()
                call_window.title('Chamada recebida')
                call_label = tk.Label(call_window, text='Chamada recebida de ' + message.split(',')[0])
                call_label.pack(side=tk.TOP)
                accept_button = tk.Button(call_window, text='Aceitar', command=lambda: call_window.quit())
                accept_button.pack(side=tk.LEFT)
                call_window.mainloop()
                call_window.destroy()
                self.accept_call(conn)
                self.start_call(message.split(',')[1])
                break
            if message.startswith('accept'):
                print('Chamada aceita')
                self.start_call(message.split(',')[1])
                break
            elif message == 'reject':
                print('Chamada rejeitada')
        

    def start_call(self, ip):
        print('Iniciando chamada para ' + ip)
        print('Iniciando servidor de streaming no IP ' + self.ip)
        streaming_server = StreamingServer(self.ip, 9999)
        camera_client = CameraClient(ip, 9999)
        audio_sender = AudioSender(ip, 8888)
        audio_receiver = AudioReceiver(self.ip, 8888)
        threading.Thread(target=streaming_server.start_server).start()
        threading.Thread(target=audio_receiver.start_server).start()
        time.sleep(1)
        threading.Thread(target=camera_client.start_stream).start()
        threading.Thread(target=audio_sender.start_stream).start()
        
    def accept_call(self, conn):
        conn.send(f'accept,{self.ip}'.encode())

    def reject_call(self, conn):
        conn.send('reject'.encode())

    # Define um método para executar a interface do usuário
    def run(self):
        self.root.mainloop()

# Se este script for o principal, solicita o nome e a porta de chamada do usuário, cria um novo cliente, registra o cliente no servidor e executa a interface do usuário
if __name__ == "__main__":
    # Abre uma janela Tkinter para obter o nome e a porta de chamada do usuário
    root = tk.Tk()
    root.title('Chat Client')
    # Cria um rótulo para o nome do usuário
    name_label = tk.Label(root, text='Nome')
    name_label.pack(side=tk.TOP)
    # Cria uma caixa de texto para o nome do usuário
    name_entry = tk.Entry(root)
    name_entry.pack(side=tk.TOP)
    # Cria um rótulo para a porta de chamada do usuário
    client_call_port_label = tk.Label(root, text='Porta de chamada')
    client_call_port_label.pack(side=tk.TOP)
    # Cria uma caixa de texto para a porta de chamada do usuário
    client_call_port_entry = tk.Entry(root)
    client_call_port_entry.pack(side=tk.TOP)
    
    # Cria um botão para registrar o usuário, quando clicado deve obter o nome e a porta de chamada, e atribuir esses valores as variáveis name e client_call_port, respectivamente, e encerrar a janela
    register_button = tk.Button(root, text='Registrar', command=lambda: root.quit())
    register_button.pack(side=tk.TOP)
    # Inicia a interface do usuário
    root.mainloop()
    # Obtém o nome e a porta de chamada do usuário
    name = name_entry.get()
    client_call_port = int(client_call_port_entry.get())
    # Encerra a janela de registro
    root.destroy()

    # Inicia a janela do sistema principal
    client = ChatClient(client_call_port)
    client.register(name, client_call_port)
    client.run()