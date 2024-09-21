import socket
from abc import abstractmethod

from game.messages.common import CoupMessage


class Connection:
    @abstractmethod
    def send(self, msg: CoupMessage):
        raise NotImplementedError()

    @abstractmethod
    def receive(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def send_and_receive(self, msg: CoupMessage) -> str:
        raise NotImplementedError()

    @abstractmethod
    def close(self):
        raise NotImplementedError()


class OpenSocket(Connection):
    @classmethod
    def new(cls, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        return cls(sock)

    def __init__(self, connection):
        self.connection = connection

    def send(self, msg: CoupMessage):
        self.connection.sendall(msg.serialize().encode("UTF-8"))

    def receive(self) -> str:
        return self.connection.recv(1024).decode("UTF-8")

    def send_and_receive(self, msg: CoupMessage) -> str:
        self.send(msg)
        return self.receive()

    def close(self):
        self.connection.close()
