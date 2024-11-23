import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

# Server Configuration
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 1234

# UI Appearance
BACKGROUND = '#282C34'
HIGHLIGHT = '#61AFEF'
TEXT_COLOR = 'white'
FONT_MAIN = ("Courier New", 14)
FONT_BUTTON = ("Courier New", 12)
FONT_CHAT = ("Courier New", 12)

# Client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def append_message(msg):
    """Adds a message to the chat display."""
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, f"{msg}\n")
    chat_display.config(state=tk.DISABLED)


def connect_to_server():
    """Establishes a connection to the server."""
    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        append_message("[SERVER] Connected successfully!")
    except Exception as e:
        messagebox.showerror("Connection Error", f"Failed to connect: {e}")
        return

    user_name = username_entry.get()
    if user_name:
        client_socket.send(user_name.encode('utf-8'))
    else:
        messagebox.showerror("Invalid Input", "Username cannot be empty")
        return

    username_entry.config(state=tk.DISABLED)
    connect_button.config(state=tk.DISABLED)

    threading.Thread(target=receive_messages).start()


def send_message():
    """Sends a message to the server."""
    msg = message_entry.get()
    if msg:
        client_socket.send(msg.encode('utf-8'))
        message_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Input Error", "Cannot send an empty message.")


def receive_messages():
    """Receives messages from the server."""
    while True:
        try:
            msg = client_socket.recv(2048).decode('utf-8')
            if msg:
                user, content = msg.split("~", 1)
                append_message(f"[{user}] {content}")
            else:
                append_message("[SERVER] Received empty message.")
        except Exception as e:
            append_message(f"[SERVER] Error: {e}")
            break


# Building the GUI
root = tk.Tk()
root.title("Chat Application")
root.geometry("600x600")
root.configure(bg=BACKGROUND)

# Top Section
top_frame = tk.Frame(root, bg=BACKGROUND)
top_frame.pack(pady=10)

tk.Label(top_frame, text="Username:", bg=BACKGROUND, fg=TEXT_COLOR, font=FONT_MAIN).pack(side=tk.LEFT, padx=5)
username_entry = tk.Entry(top_frame, font=FONT_MAIN, bg='black', fg=TEXT_COLOR, width=20)
username_entry.pack(side=tk.LEFT, padx=5)

connect_button = tk.Button(top_frame, text="Connect", bg=HIGHLIGHT, fg='black', font=FONT_BUTTON, command=connect_to_server)
connect_button.pack(side=tk.LEFT, padx=10)

# Chat Display
chat_display = scrolledtext.ScrolledText(root, bg='black', fg=TEXT_COLOR, font=FONT_CHAT, width=70, height=25)
chat_display.pack(pady=10)
chat_display.config(state=tk.DISABLED)

# Bottom Section
bottom_frame = tk.Frame(root, bg=BACKGROUND)
bottom_frame.pack(pady=10)

message_entry = tk.Entry(bottom_frame, font=FONT_MAIN, bg='black', fg=TEXT_COLOR, width=50)
message_entry.pack(side=tk.LEFT, padx=5)

send_button = tk.Button(bottom_frame, text="Send", bg=HIGHLIGHT, fg='black', font=FONT_BUTTON, command=send_message)
send_button.pack(side=tk.LEFT, padx=5)

# Run the GUI
root.mainloop()
