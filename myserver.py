import threading
import socket


class Chatroom:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.server = None
        self.clients = []
        self.names = []
        self.initMessages = []
        self.conns = []

    def displayMessage(self, message):  # when receiving a message, send it to everyone in the room
        for client in self.clients:
            print(self.names)
            client.send(message.encode())

    def run(self):  # run : initializes the server, then listens and creates new threads for each server found
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.address, self.port))  # bind our address to the socket for the server
        self.server.listen()  # listen for the client now

        while 1:
            conn, address = self.server.accept()  # take in the connection name and address of the client
            # connection.send([string].encode)
            # connection.receive([string].decode)
            thread = threading.Thread(target=self.service, args=[conn])  # create a new thread to service the new client
            thread.start()
        return

    def service(self, conn):  # services a new client by continuously accepting messages
        conn.send('NAME¤'.encode())  # send an encoded request for name
        self.clients.append(conn)
        name = conn.recv(1024).decode()
        self.names.append(name)
        self.conns.append(conn)
        while 1:
            try:
                message = conn.recv(1024).decode()
                if "¤" in message:  # use a reserved system keyword to handle KILL requests (and other requests if I get around to them)
                    if message == "¤KILL":
                        conn.send("KILL¤".encode())
                        self.displayMessage("{} is leaving the chat!".format(self.names[self.clients.index(conn)]))
                        self.names.remove(self.names[self.clients.index(conn)])
                        self.clients.remove(conn)
                        break
                elif message[0] == "/":  # reserved command for user inputs like /nick
                    if "/nick" in message:
                        self.names[self.clients.index(conn)] = message[6:]
                        conn.send("NICK¤".encode())  # send a system message saying name was changed
                else:   # handle standard messages by displaying them to everyone
                    message = "{}: {}".format(self.names[self.clients.index(conn)], message)
                    self.displayMessage(message)

            except:  # case that our connection breaks
                self.clients.remove(conn)
                break
        self.conns.remove(conn) # handling ending connections
        conn.close()
        return

# begin by initializing our server and address, initialized on the localhost's IP address with port 2213.
validHost = False
adr = input(
    "Please input a host address: (press the return button without typing anything to use the default [your server's IP address]")
if len(adr) == 0:
    adr = socket.gethostname()
port = input(
    "Please input the port you want to use: (press the return button without typing anything to use the default of 5000")
if len(port) == 0:
    port = 5000
while not validHost:
    try:
        port = int(port)
        adr = socket.gethostbyname(adr)
        cr = Chatroom(adr, port)
        validHost = True
    except:
        adr = input("Please re-enter your host address (make sure it's valid!)")
        port = input("Please re-enter your port number (make sure it's valid!)")
        validHost = False
if validHost:
    print("Make sure clients are connecting to host {} at port {}".format(socket.gethostbyname(adr), port))
cr.run()
