import socket
from abc import abstractmethod

from config import PARAM_SPLITTER, COMMAND_END

class Connection:
    @abstractmethod
    def send(self, *msg):
        raise NotImplementedError()

    @abstractmethod
    def receive(self):
        raise NotImplementedError()

    @abstractmethod
    def send_and_receive(self, *msg):
        raise NotImplementedError()

    @abstractmethod
    def close(self, *msg):
        raise NotImplementedError()


class OpenSocket(Connection):
    @classmethod
    def new(cls, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        return cls(sock)

    def __init__(self, connection):
        self.connection = connection

    def send(self, *msg):
        self.connection.sendall((PARAM_SPLITTER.join([str(m) for m in msg]) + COMMAND_END).encode("UTF-8"))

    def receive(self):
        return self.connection.recv(1024).decode("UTF-8")

    def send_and_receive(self, *msg):
        self.send(*msg)
        return self.receive()

    def close(self):
        self.connection.close()
