import socket
import tkinter as tk

# Cria um socket TCP/IP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define o endereço e porta do servidor
server_address = ('localhost', 3000)

# Conecta o socket ao servidor
client_socket.connect(server_address)

# Obtém o IP e porta do cliente
ip, port = client_socket.getsockname()

# Envia uma mensagem de registro para o servidor
name = input('Enter your name: ')
message = ','.join([name, ip, str(port)])
client_socket.send(message.encode())

# Recebe uma resposta do servidor
response = client_socket.recv(1024).decode()
print(response)

# Cria a interface gráfica
root = tk.Tk()
root.title('Chat Client')

# Cria o botão de consulta de usuários
list_button = tk.Button(root, text='Consultar usuários', command=lambda: show_user_list())
list_button.pack(side=tk.LEFT)

# Cria o botão de encerramento da conexão
quit_button = tk.Button(root, text='Encerrar conexão', command=lambda: send_message('quit'))
quit_button.pack(side=tk.LEFT)

# Cria a tabela de usuários
user_list = tk.Listbox(root)
user_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Cria o botão de fechar a janela de detalhes do usuário
close_button = tk.Button(root, text='Fechar', command=lambda: detail_window.destroy())

# Exibe a lista de usuários
# Exibe a lista de usuários
def show_user_list():
    global user_list

    # Envia uma mensagem de consulta de usuários para o servidor
    send_message('list')

    # Recebe a lista de usuários do servidor
    response = client_socket.recv(1024).decode()
    user_list.delete(0, tk.END)

    # Adiciona os usuários à lista
    for user in response.split(','):
        user_list.insert(tk.END, user)

    # Atualiza a interface gráfica
    root.update()
# Exibe os detalhes de um usuário
def show_user_details(user):
    global detail_window
    global close_button

    # Envia uma mensagem de consulta de detalhes para o servidor
    send_message(f'details,{user}')

    # Recebe os detalhes do usuário do servidor
    response = client_socket.recv(1024).decode()
    ip, port = response.split(',')

    # Cria a janela de detalhes do usuário
    detail_window = tk.Toplevel(root)
    detail_window.title(f"Detalhes de {user}")
    detail_label = tk.Label(detail_window, text=f"IP: {ip}\nPorta: {port}")
    detail_label.pack(side=tk.TOP)
    close_button.pack(side=tk.BOTTOM)

# Envia mensagens para o servidor
def send_message(message):
    global client_socket

    client_socket.send(message.encode())

    if message == 'quit':
        response = client_socket.recv(1024).decode()
        print(response)
        client_socket.close()
        root.quit()

root.mainloop()