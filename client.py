import threading
from tkinter import *
from tkinter import simpledialog

import grpc

import proto.chat_pb2 as chat
import proto.chat_pb2_grpc as rpc

address = 'localhost'
port = 11912


class Client:

    def __init__(self, u: str, module_id: str, subsection_id: str, window):
        # the frame to put UI components on
        self.window = window
        self.username = u
        self.module_id = module_id
        self.subsection_id = subsection_id

        # create a gRPC channel + stub
        channel = grpc.insecure_channel(address + ':' + str(port))
        self.conn = rpc.ChatServerStub(channel)

        # create a new listening thread for when new message streams come in
        threading.Thread(target=self._listen_for_messages, daemon=True).start()

        self._setup_ui()
        self.window.mainloop()

    def _listen_for_messages(self):
        """
        This method will be run in a separate thread as the main/UI thread,
        because the for-in call is blocking when waiting for new messages.
        """
        for note in self.conn.ChatStream(chat.Empty()):
            print("R[{}] {}: {}: {}".format(note.name, note.id, note.title, note.content))
            message = "[{}] {}: {}: {}\n".format(note.name, note.id, note.title, note.content)
            self.chat_list.insert(END, message)
            # Add the following line to ensure the UI is updated immediately
            self.chat_list.update_idletasks()

    def send_message(self, event):
        """
        This method is called when the user enters something into the textbox.
        """
        message = self.entry_message.get()
        if message:
            n = chat.Note()
            n.name = self.username
            n.id = self.module_id
            n.title = self.subsection_id
            n.content = message
            print("S[{}] {}: {}: {}".format(n.name, n.id, n.title, n.content))
            self.conn.SendNote(n)

    def _setup_ui(self):
        self.chat_list = Text()
        self.chat_list.pack(side=TOP)
        self.lbl_username = Label(self.window, text=self.username)
        self.lbl_username.pack(side=LEFT)
        self.entry_message = Entry(self.window, bd=5)
        self.entry_message.bind('<Return>', self.send_message)
        self.entry_message.focus()
        self.entry_message.pack(side=BOTTOM)


if __name__ == '__main__':
    root = Tk()
    frame = Frame(root, width=300, height=300)
    frame.pack()
    root.withdraw()

    # Ask the user for username, module_id, and subsection_id
    username = simpledialog.askstring("Username", "What's your username?", parent=root)
    module_id = simpledialog.askstring("Module ID", "Enter Module ID:", parent=root)
    subsection_id = simpledialog.askstring("Subsection ID", "Enter Subsection ID:", parent=root)

    root.deiconify()
    c = Client(username, module_id, subsection_id, frame)
