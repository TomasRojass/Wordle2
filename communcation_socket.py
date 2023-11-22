import socket
import json


class CommuncationSocket:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.queue_responses = []
        self.gamestate = ""

    def connect(self):
        self.sock.connect((self.host, self.port))

    def close_connection(self):
        self.sock.close()

    def send(self, tipo, contenido):
        # Enviar mensaje al servidor
        self._send_message(tipo, contenido)

    def receive(self):
        data = self.sock.recv(1024)
        respuesta = json.loads(data.decode())
        self._parse(respuesta["type"], respuesta["content"])

    def _send_message(self, tipo, contenido):
        mensaje = {"Type": tipo, "Content": contenido}
        mensaje_json = json.dumps(mensaje)
        self.sock.sendall(mensaje_json.encode())

    def _parse(self, tipo, contenido):
        print(tipo, contenido)
        if tipo == "AttemptResponse":
            self.queue_responses.append(contenido)
        elif tipo == "GameState":
            self.gamestate = contenido
