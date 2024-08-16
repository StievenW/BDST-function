import os
import time
import threading
import queue
import tkinter as tk
from tkinter import scrolledtext
import struct
import socket
import config  # Import the config file

# RCON Packet Types
RCON_PACKET_TYPE = {
    'SERVERDATA_AUTH': 3,
    'SERVERDATA_AUTH_RESPONSE': 2,
    'SERVERDATA_EXECCOMMAND': 2,
    'SERVERDATA_RESPONSE_VALUE': 0
}

def send_packet(client_socket, packet_type, request_id, body=''):
    size = len(body) + 14
    packet = struct.pack(
        '<III', size - 4, request_id, packet_type
    ) + body.encode('ascii') + b'\x00\x00'
    client_socket.sendall(packet)

def recv_packet(client_socket):
    def recv_bytes(sock, num_bytes):
        buffer = b''
        while len(buffer) < num_bytes:
            fragment = sock.recv(num_bytes - len(buffer))
            if not fragment:
                raise ConnectionResetError("Connection closed")
            buffer += fragment
        return buffer

    size = struct.unpack('<I', recv_bytes(client_socket, 4))[0]
    request_id = struct.unpack('<I', recv_bytes(client_socket, 4))[0]
    packet_type = struct.unpack('<I', recv_bytes(client_socket, 4))[0]
    body = recv_bytes(client_socket, size - 10).decode('ascii')
    recv_bytes(client_socket, 2)
    
    return request_id, packet_type, body

def connect_rcon():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((config.HOST, config.PORT))  # Use config values

    # Authenticate
    send_packet(client_socket, RCON_PACKET_TYPE['SERVERDATA_AUTH'], 1, config.PASSWORD)  # Use config value
    _, packet_type, _ = recv_packet(client_socket)
    if packet_type != RCON_PACKET_TYPE['SERVERDATA_AUTH_RESPONSE']:
        raise Exception("RCON Authentication failed")
    
    return client_socket

def send_rcon_command(client_socket, command):
    send_packet(client_socket, RCON_PACKET_TYPE['SERVERDATA_EXECCOMMAND'], 2, command)
    _, _, response = recv_packet(client_socket)
    return response

def update_file_list(file_list_box, functions_folder):
    file_list_box.delete(0, tk.END)
    for filename in os.listdir(functions_folder):
        if filename.endswith('.mcfunction'):
            file_list_box.insert(tk.END, filename)

def monitor_functions_folder(input_queue, functions_folder, stop_event, file_list_box):
    while not stop_event.is_set():
        update_file_list(file_list_box, functions_folder)
        all_commands = []
        for root, dirs, files in os.walk(functions_folder):
            for filename in files:
                if filename.endswith('.mcfunction'):
                    filepath = os.path.join(root, filename)
                    with open(filepath, 'r') as file:
                        commands = file.read().splitlines()
                        for command in commands:
                            command = command.strip()
                            if command and not command.startswith('#'):
                                all_commands.append(command)
        for command in all_commands:
            input_queue.put(command)
        time.sleep(5)  # Sleep for 5 seconds before scanning the folder again

def execute_commands(input_queue, stop_event, log_box, command_delay):
    client_socket = connect_rcon()
    commands = []

    try:
        while not stop_event.is_set():
            if not commands:
                while not input_queue.empty():
                    command = input_queue.get()
                    if command:
                        commands.append(command)

            if commands:
                last_command_time = time.time()
                for command in commands:
                    if stop_event.is_set():
                        break
                    current_time = time.time()
                    time_since_last_command = current_time - last_command_time

                    # Ensure a minimum delay
                    if time_since_last_command < command_delay:
                        time.sleep(command_delay - time_since_last_command)

                    response = send_rcon_command(client_socket, command)
                    log_box.config(state=tk.NORMAL)
                    log_box.insert(tk.END, f"Executed: {command}, Response: {response}\n")
                    log_box.yview(tk.END)
                    log_box.config(state=tk.DISABLED)
                    last_command_time = time.time()

                # Commands list is requeued to run again
            else:
                time.sleep(0.1)  # Sleep for 100 milliseconds if no commands are available

    finally:
        client_socket.close()

def start_processes(input_queue, functions_folder, file_list_box, log_box, start_button, stop_event, command_delay):
    start_button.config(state=tk.DISABLED)
    stop_event.clear()

    # Start monitoring functions folder thread
    monitor_thread = threading.Thread(target=monitor_functions_folder, args=(input_queue, functions_folder, stop_event, file_list_box))
    monitor_thread.daemon = True
    monitor_thread.start()

    # Start executing commands thread
    execute_thread = threading.Thread(target=execute_commands, args=(input_queue, stop_event, log_box, command_delay))
    execute_thread.daemon = True
    execute_thread.start()

def stop_processes(start_button, stop_event):
    stop_event.set()
    start_button.config(state=tk.NORMAL)

def create_gui(functions_folder):
    root = tk.Tk()
    root.title("MCFunction RCON Controller")

    file_list_box = tk.Listbox(root, height=10, width=50)
    file_list_box.pack(padx=10, pady=10)

    log_box = scrolledtext.ScrolledText(root, state='disabled', height=10, width=100)
    log_box.configure(font='TkFixedFont')
    log_box.pack(padx=10, pady=10)

    input_queue = queue.Queue()
    stop_event = threading.Event()

    # Create a variable to store command delay
    command_delay = tk.DoubleVar(value=0.06)  # Set default delay to 60 milliseconds

    def on_start():
        start_processes(input_queue, functions_folder, file_list_box, log_box, start_button, stop_event, command_delay.get())

    def on_stop():
        stop_processes(start_button, stop_event)

    start_button = tk.Button(root, text="Start", command=on_start)
    start_button.pack(side=tk.LEFT, padx=10)

    stop_button = tk.Button(root, text="Stop", command=on_stop)
    stop_button.pack(side=tk.RIGHT, padx=10)

    # Create a scale to adjust command delay with the new range from 0.06 to 0.1
    delay_scale = tk.Scale(root, from_=0.06, to=0.1, resolution=0.001, orient=tk.HORIZONTAL, label="Command Delay (seconds)", variable=command_delay)
    delay_scale.pack(padx=10, pady=10)

    update_file_list(file_list_box, functions_folder)

    root.mainloop()

if __name__ == '__main__':
    functions_folder = 'functions'  # Change this to your 'functions' folder path
    create_gui(functions_folder)
