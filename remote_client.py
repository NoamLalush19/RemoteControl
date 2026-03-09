import socket
import threading
from tkinter import Tk, Label
from PIL import Image, ImageTk
from io import BytesIO
import struct

HOST = '127.0.0.1'
PORT = 12345                                  

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

root = Tk()
root.title("Remote Client")
label = Label(root)
label.pack()


def send_to_server(type_char, message):
    try:
        data = message.encode()
        packet = type_char + struct.pack('!I', len(data)) + data
        client_socket.sendall(packet)
    except:
        pass

label.bind("<Button-1>", lambda e: send_to_server(b'C', f"{e.x} {e.y}")) 
root.bind("<Key>", lambda e: send_to_server(b'K', e.char))             

def recv_all(conn, n):
    data = b''
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet: return None
        data += packet
    return data

def receive():
    while True:
        try:
            type_byte = recv_all(client_socket, 1)
            if not type_byte: break
            
            data_len_bytes = recv_all(client_socket, 4)
            if not data_len_bytes: break
            data_len = struct.unpack('!I', data_len_bytes)[0]
            
            data = recv_all(client_socket, data_len)
            if data is None: break

            if type_byte == b'S': # קבלת מסך מהשרת
                image = Image.open(BytesIO(data))
                photo = ImageTk.PhotoImage(image)
                label.config(image=photo)
                label.image = photo
        except Exception as e:
            print(f"Error: {e}")
            break

threading.Thread(target=receive, daemon=True).start()
root.mainloop()
