import socket
import json

class CommuncationSocket:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.sock.connect((self.host, self.port))

    def close_connection(self):
        self.sock.close()

    def send_and_receive(self, tipo, contenido):
        # Enviar mensaje al servidor
        self._send_message(tipo, contenido)
        
        # Recibir y decodificar la respuesta
        data = self.sock.recv(1024)
        respuesta = json.loads(data.decode())
        return respuesta

    def _send_message(self, tipo, contenido):
        mensaje = {"Type": tipo, "Content": contenido}
        mensaje_json = json.dumps(mensaje)
        self.sock.sendall(mensaje_json.encode())