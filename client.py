import socket
import tkinter as tk

class ChatClient:
    def __init__(self, server_address=('localhost', 3001)):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(server_address)
        self.ip, self.port = self.client_socket.getsockname()
        self.root = tk.Tk()
        self.root.title('Chat Client')
        self.user_list = tk.Listbox(self.root)
        self.user_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.user_list.bind('<Double-1>', self.callback)

        self.list_button = tk.Button(self.root, text='Consultar usuários', command=self.show_user_list)
        self.list_button.pack(side=tk.LEFT)

        self.quit_button = tk.Button(self.root, text='Encerrar conexão', command=lambda: self.send_message('quit'))
        self.quit_button.pack(side=tk.LEFT)

    def register(self, name, client_call_port):
        message = ','.join([name, self.ip, str(self.port), str(client_call_port)])
        self.client_socket.send(message.encode())
        response = self.client_socket.recv(1024).decode().split(',')
        print(response[1])
        if response[0] == 'error':
            self.client_socket.close()
            exit()

    def callback(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            data = event.widget.get(index)
            self.show_user_details(data)

    def show_user_list(self):
        self.send_message('list')
        response = self.client_socket.recv(1024).decode()
        self.user_list.delete(0, tk.END)
        for user in response.split(','):
            self.user_list.insert(tk.END, user)
        self.root.update()

    def show_user_details(self, user):
        self.send_message(f'details,{user}')
        response = self.client_socket.recv(1024).decode()
        ip, port = response.split(',')
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Detalhes de {user}")
        detail_label = tk.Label(detail_window, text=f"IP: {ip}\nPorta: {port}")
        detail_label.pack(side=tk.TOP)

    def send_message(self, message):
        self.client_socket.send(message.encode())
        if message == 'quit':
            response = self.client_socket.recv(1024).decode()
            print(response)
            self.client_socket.close()
            self.root.quit()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    name = input('Qual o seu nome? ')
    client_call_port = int(input('Qual porta que você deseja usar para receber chamadas? '))
    client = ChatClient()
    client.register(name, client_call_port)
    client.run()