import tkinter as tk
from client import Client
from controller import Controller
from gui import View

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chat Client")

        client = Client(('localhost', 3001))
        view = View(self)
        controller = Controller(client, view)
        controller.start()

if __name__ == "__main__":
    app = App()