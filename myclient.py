import threading
import socket
from tkinter import *
from tkinter import ttk, messagebox
import sys

interfaces = []


class Client:
    def __init__(self, address, port):  # Initializes our clients with various attributes
        self.address = address
        self.port = port
        self.client = None
        self.name = ''
        self.messages = []  # empty list of messages

    def connect(self):  # setup an initial connection with the server, then use setname() to initiate communication
        # . If the server can't be reached, exit
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.address, self.port))
            self.sendname()
        except:
            messagebox.showerror("Error",
                                 "Either the host is not connected to the requested socket, or the requested socket is invalid. Now forcing the termination of the client process.")
            if len(interfaces) > 0:
                interfaces[0].destroy()
            sys.exit()

    def setName(self, name):  # updates the user's name
        self.name = name

    def sendname(self):  # command used to set up a connection. Wait on server's name request, then send the name
        test = self.client.recv(1024)

        if test.decode() == 'NAME¤':
            self.client.send(self.name.encode())

    def chat(self):  # once we're ready to start chatting, create a new thread to recieve messages

        receievethread = threading.Thread(target=self.receiver,
                                          args=[])
        receievethread.start()

    def sender(self, message):  # basic sender that's called whenever we have a message to send
        while 1:
            self.client.send(message.encode())
            break

    def exit(self):  # sends a kill request to the server
        self.client.send("¤KILL".encode())
        return ()

    def sendMessage(self, message):  # whenever we have a message to send, create a new thread to send the message
        sendthread = threading.Thread(target=self.sender,
                                      args=[message])
        sendthread.start()

    def receiver(self):  # reciever, handles receiving messages back from the server by putting them in a list
        while 1:
            received = self.client.recv(1024).decode()
            self.messages.append(received)  # we always want this message in so all of our threads can handle events
            if "¤" in received:  # event handler
                if received == "KILL¤":  # in the case of a kill command, we break the loop so the thread exits
                    break
        sys.exit("exited receiver thread")


class GUI:  # our GUI class, used to create our TKInter UI
    def __init__(self, client):
        self.client = client
        self.processes = []
        self.ChatRoom = Tk()  # initialize Chatroom as our base window, and hide it
        self.ChatRoom.title("Chatroom")
        interfaces.append(self.ChatRoom)
        self.ChatRoom.geometry("960x540")
        self.ChatRoom.withdraw()
        self.NameInput = Toplevel()  # create a top level instance to retrieve the user's name
        self.NameInput.title("Input Name")
        self.L1 = Label(self.NameInput, text="Please enter your display name: ")
        self.L1.pack(side=LEFT)
        self.B1 = Button(self.NameInput, text="Submit", command=lambda: self.setName())  # button to submit name
        self.B1.pack(side=RIGHT)
        self.E1 = Entry(self.NameInput, bd=5)

        self.E1.pack(side=RIGHT)
        self.E1.bind("<Return>", lambda x: self.setName())  # allows pressing enter to submit name
        self.ChatRoom.mainloop()

    def setName(self):  # handles errors for the name and then sends name to the client, then deletes the name input window and creates a chat room
        self.name = self.E1.get()
        if len(self.name) <= 0:
            messagebox.showerror("Error", "Your name must be at least 1 character long")
            return ()
        self.client.setName(self.name)
        self.NameInput.destroy()
        self.makeChatRoom()

    def makeChatRoom(self):  # creates our chatroom
        self.client.connect()
        self.ChatRoom.protocol("WM_DELETE_WINDOW", self.closeWindow)  # procedure for handling exits
        dispMsg = threading.Thread(target=self.dispMsg,
                                   args=[])
        dispMsg.start()
        self.ChatRoom.deiconify()
        self.ChatRoom.title("The chatroom.")
        self.enterMsg = Entry(self.ChatRoom, bd=5)  # our widget for entering text to chat with
        self.enterMsg.place(relheight=.06, relwidth=.74, relx=.02, rely=.89)
        self.enterButton = Button(self.ChatRoom, text="Submit", command=lambda: self.sendMessage(), bd=5) # widget to allow us to sumbit messages
        self.enterMsg.bind("<Return>", lambda x: self.sendMessage())    # allows us to press enter to send messages
        self.text = Text(self.ChatRoom) # our widget for displaying messages
        self.text.configure(state="disabled")

        self.enterButton.place(relx=0.77, rely=0.89, relheight=0.06, relwidth=0.22)

        self.text.place(relheight=0.8,
                        relwidth=1,
                        rely=0.08)

    def closeWindow(self):  # when the chatroom is closed, handles program termination
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            interfaces.remove(self.ChatRoom)
            self.ChatRoom.destroy()
            self.client.exit()

    def sendMessage(self):  # message handler to send messages from entry
        message = self.enterMsg.get()
        self.enterMsg.delete(0, END)
        if "/nick" in message:
            self.client.setName(message[6:])
        if "¤" in message:  # prevents user from putting key symbol in chat, reserved for system messages
            messagebox.showinfo("Error", "¤ is a reserved character")
        else:
            self.client.sendMessage(message)

    def dispMsg(self):  # a method used in another thread to constantly extract strings and add them to the textbox
        self.client.chat()
        while 1:
            if (len(self.client.messages)) > 0:
                msg = self.client.messages.pop(-1)
                if "¤" in msg:
                    if msg == "KILL¤":
                        break
                    else:  # we ignore message with system calls
                        continue
                else:
                    self.text.configure(state="normal")
                    self.text.insert(END, msg + "\n")
                    self.text.see(END)
                    self.text.configure(state="disabled")

        # sys.exit("exited display thread")
        return ()


#    def displayMessages(self):

class initConnection:   #our class used to intialize the client, creates a TKinter window that prompts for host address and port
    def __init__(self):
        self.inputs = Tk()
        interfaces.append(self.inputs)
        self.E1 = Entry(self.inputs)
        self.E2 = Entry(self.inputs)
        self.B1 = Button(self.inputs, bd=5, text="Submit", command=lambda: self.checkVals())
        self.L1 = Label(self.inputs, text="Please input the host address")
        self.L2 = Label(self.inputs, text="Please input the port")
        self.L1.grid(column=0, row=0)
        self.L2.grid(column=0, row=1)
        self.B1.grid(column=2, row=0, rowspan=1)
        self.E1.grid(column=1, row=0)
        self.E2.grid(column=1, row=1)
        self.inputs.bind("<Return>", lambda x: self.checkVals)
        self.inputs.title("Connection Inputs")
        self.inputs.mainloop()

    def checkVals(self):    #tries to ensure a connection can be established, then calls the GUI class
        try:
            cl = Client(socket.gethostbyname(self.E1.get()), int(self.E2.get()))
            interfaces.remove(self.inputs)
            self.inputs.destroy()
            g = GUI(cl)
            return
        except:
            messagebox.showerror("Error", "Either the host address or the port are invalid")
            return


init = initConnection() # main

