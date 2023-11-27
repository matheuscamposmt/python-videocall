import tkinter as tk
from client import Client
from controller import Controller
from gui import View
from threading import Thread

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chat Client")

        client = Client(('localhost', 3001))
        view = View(self)
        controller = Controller(client, view)
        call_thread = Thread(target=client.receive_call)
        call_thread.start()
        controller.start()

if __name__ == "__main__":
    app = App()