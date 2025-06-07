import threading

class ClientHandler(threading.Thread):
    def __init__(self, client_socket, address):
        super().__init__()
        self.client_socket = client_socket
        self.address = address

    def run(self):
        try:
            self.client_socket.sendall(b"220 Welcome to FTPServer\r\n")
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                self.client_socket.sendall(b"500 Command not implemented\r\n")
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            self.client_socket.close()
