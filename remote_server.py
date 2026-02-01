import socket  
import threading
import struct
from PIL import ImageGrab
from io import BytesIO
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController
import time

HOST = '0.0.0.0'
PORT = 12345

mouse = MouseController()
keyboard = KeyboardController()
clients = []

def recv_all(conn, n):
    data = b''
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def handle_client_commands(conn):
    try:
        while True:
            type_byte = recv_all(conn, 1)
            if not type_byte: break
            
            data_len_bytes = recv_all(conn, 4)
            if not data_len_bytes: break
            data_len = struct.unpack('!I', data_len_bytes)[0]
            
            data_bytes = recv_all(conn, data_len)
            if not data_bytes: break
            data = data_bytes.decode()

            if type_byte == b'K':
                keyboard.type(data)
            elif type_byte == b'C':
                try:
                    x, y = map(int, data.split())
                    mouse.position = (x, y)
                    mouse.click(Button.left)
                except ValueError: pass
            elif type_byte == b'M':
                try:
                    x, y = map(int, data.split())
                    mouse.position = (x, y)
                except ValueError: pass
    except:
        pass
    finally:
        if conn in clients:
            clients.remove(conn)
        conn.close()

def send_screen():
    while True:
        if not clients:
            time.sleep(1)
            continue
        try:
            screenshot = ImageGrab.grab()
            buf = BytesIO()
            screenshot.save(buf, format='JPEG', quality=50)
            img_data = buf.getvalue()
            
            packet = b'S' + struct.pack('!I', len(img_data)) + img_data
            for c in clients[:]:
                try:
                    c.sendall(packet)
                except:
                    if c in clients: clients.remove(c)
            time.sleep(0.1) 
        except:
            pass

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)

threading.Thread(target=send_screen, daemon=True).start()

print(f"[SERVER] Listening on {HOST}:{PORT}...")
while True:
    conn, addr = server.accept()
    clients.append(conn)
    threading.Thread(target=handle_client_commands, args=(conn,), daemon=True).start()