from gui import View, SignUpView, UserListView
from client import Client
from tkinter import ACTIVE

class Controller:
    def __init__(self, client: Client, gui: View):
        self.client = client
        self.gui = gui
        self.signup_controller = SignUpController(client, gui)
        self.userlist_controller = UserListController(client, gui)

    def quit(self):
        self.client.quit()
        self.gui.root.quit()

    def start(self):
        self.gui.root.mainloop()

class SignUpController:
    def __init__(self, client: Client, view: View):
        self.client = client
        self.view = view
        self.frame: SignUpView = self.view.frames["signup"]
        self._bind()
    
    def _bind(self):
        self.frame.register_button.configure(command=self.register)
        self.frame.quit_button.configure(command=self.quit)

    def register(self):
        name = self.frame.username_entry.get()
        client_call_port = int(self.frame.port_entry.get())
        self.client.register(name, client_call_port)
        if self.client.registered:
            self.view.switch("userlist")

    def quit(self):
        self.view.root.quit()
 

class UserListController:
    def __init__(self, client: Client, view: View):
        self.client = client
        self.view = view
        self.frame: UserListView = self.view.frames["userlist"]
        self._bind()

    def _bind(self):
        self.frame.user_list.bind('<Double-1>', self.user_selection_callback)
        self.frame.list_button.configure(command=self.show_user_list)
        self.frame.quit_button.configure(command=self.quit)

    def register(self, name, client_call_port):
        self.client.register(name, client_call_port)

        user_list = self.client.get_user_list()
        if user_list:
            self.frame.update_user_list(user_list)

    def show_user_details(self, user):
        data = self.client.get_user_details(user)
        self.frame.window_user_details(data)

    def call_user(self):
        user = self.frame.user_list.get(ACTIVE)
        self.client.call_user(user)

    def show_user_list(self):
        user_list = self.client.get_user_list()
        if user_list:
            self.frame.update_user_list(user_list)

    def user_selection_callback(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            data = event.widget.get(index)
            self.show_user_details(data)
    
    def quit(self):
        self.client.quit()
        self.view.root.quit()