import socket
import tkinter as tk

# Define a classe ChatClient
class ChatClient:
    # Inicializa o cliente com o endereço do servidor padrão ('localhost', 3001)
    def __init__(self, server_address=('localhost', 3001)):
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
        self.quit_button = tk.Button(self.root, text='Encerrar conexão', command=lambda: self.send_message('quit'))
        self.quit_button.pack(side=tk.LEFT)

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
        self.send_message('list')
        # Recebe a lista de usuários do servidor
        response = self.client_socket.recv(1024).decode()
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
        self.send_message(f'details,{user}')
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

    # Define um método para enviar uma mensagem para o servidor
    def send_message(self, message):
        # Envia a mensagem para o servidor
        self.client_socket.send(message.encode())
        # Se a mensagem for 'quit', recebe uma resposta do servidor, imprime a resposta, fecha o socket do cliente e encerra a interface do usuário
        if message == 'quit':
            response = self.client_socket.recv(1024).decode()
            print(response)
            self.client_socket.close()
            self.root.quit()

    # Define um método para executar a interface do usuário
    def run(self):
        self.root.mainloop()

# Se este script for o principal, solicita o nome e a porta de chamada do usuário, cria um novo cliente, registra o cliente no servidor e executa a interface do usuário
if __name__ == "__main__":
    name = input('Qual o seu nome? ')
    client_call_port = int(input('Qual porta que você deseja usar para receber chamadas? '))
    client = ChatClient()
    client.register(name, client_call_port)
    client.run()