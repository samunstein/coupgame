import socket

from common.common import debug_print
from config import HOST, PORT
from connection.common import OpenSocket

def get_connections(amount):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen()

    socks = []

    while len(socks) < amount:
        debug_print("Waiting for connection...")
        connect, address = sock.accept()
        connect.settimeout(10)
        socks.append(OpenSocket(connect))

    return socks
