import socket
import threading
from tkinter import Tk, Label
from PIL import Image, ImageTk
from io import BytesIO
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController, Button
import struct

HOST = '127.0.0.1'
PORT = 12345                                  

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

keyboard_controller = KeyboardController()
mouse_controller = MouseController()

root = Tk()
root.title("Remote Client")
label = Label(root)
label.pack()

def recv_all(conn, n):
    data = b''
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def receive():
    while True:
        try:
            type_byte = recv_all(client_socket, 1)
            if not type_byte:
                break

            data_len_bytes = recv_all(client_socket, 4)
            if not data_len_bytes:
                break
            
            data_len = struct.unpack('!I', data_len_bytes)[0]
            
            data = recv_all(client_socket, data_len)
            if data is None:
                break

            if type_byte == b'K':  
                key_val = data.decode()
                try:
                    keyboard_controller.press(key_val)
                    keyboard_controller.release(key_val)
                except:
                    pass
            elif type_byte == b'M':  
                x, y = map(int, data.decode().split())
                mouse_controller.position = (x, y)
            elif type_byte == b'C':  
                parts = data.decode().split()
                x, y = int(parts[0]), int(parts[1])
                button = parts[2]
                b = Button.left if 'left' in button else Button.right
                mouse_controller.position = (x, y)
                mouse_controller.click(b)
            elif type_byte == b'S':  
                image = Image.open(BytesIO(data))
                photo = ImageTk.PhotoImage(image)
                label.config(image=photo)
                label.image = photo
        except Exception as e:
            print(f"Error: {e}")
            break

threading.Thread(target=receive, daemon=True).start()
root.mainloop()