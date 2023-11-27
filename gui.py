# Define a class for the GUI
import tkinter as tk

class View:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.frames = {}

        self._add_frame(UserListView, "userlist")
        self._add_frame(SignUpView, "signup")

    def _add_frame(self, Frame, name):
        self.frames[name] = Frame(self.root)
        self.frames[name].grid(row=0, column=0, sticky="nsew")

    def switch(self, name):
        frame = self.frames[name]
        frame.tkraise()
        

class SignUpView(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create a label for the username
        self.username_label = tk.Label(self, text='Nome de usuário')
        self.username_label.pack(side=tk.TOP)

        # Create an entry for the username
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(side=tk.TOP)

        # Create a label for the password
        self.port_label = tk.Label(self, text='Porta')
        self.port_label.pack(side=tk.TOP)

        # Create an entry for the password
        self.port_entry = tk.Entry(self)
        self.port_entry.pack(side=tk.TOP)

        # Create a button to register the user
        self.register_button = tk.Button(self, text='Registrar')
        self.register_button.pack(side=tk.TOP)

        self.quit_button = tk.Button(self, text='Sair')
        self.quit_button.pack(side=tk.BOTTOM)

class UserListView(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create a list of users in the GUI
        self.user_list = tk.Listbox(self)
        self.user_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a button to query the user list
        self.list_button = tk.Button(self, text='Consultar usuários')
        self.list_button.pack(side=tk.LEFT)

        # Create a button to terminate the connection
        self.quit_button = tk.Button(self, text='Encerrar conexão')
        self.quit_button.pack(side=tk.LEFT)


    def window_user_details(self, data):
        user, ip, port = data['user'], data['ip'], data['port']
        # Cria uma nova janela para mostrar os detalhes do usuário
        detail_window = tk.Toplevel(self)
        detail_window.title(f"Detalhes de {user}")
        # Cria um rótulo para mostrar o IP e a porta do usuário
        detail_label = tk.Label(detail_window, text=f"IP: {ip}\nPorta: {port}")
        detail_label.pack(side=tk.TOP)


    def update_user_list(self, user_list):
        self.user_list.delete(0, tk.END)
        for user in user_list:
            self.user_list.insert(tk.END, user)

