import socket
import threading

# Server Configuration
SERVER_ADDRESS = '127.0.0.1'  # Localhost
SERVER_PORT = 1234            # Port for communication
MAX_CONNECTIONS = 5           # Limit for simultaneous connections
connected_users = []          # Active users with their sockets


def handle_messages(client_socket, user_name):
    """Listens for incoming messages from a client."""
    while True:
        try:
            msg = client_socket.recv(2048).decode('utf-8')
            if msg:
                send_to_all_clients(f"{user_name}~{msg}")
            else:
                print(f"Warning: Empty message received from {user_name}.")
        except ConnectionResetError:
            print(f"Lost connection with {user_name}.")
            remove_user(client_socket)
            break


def send_to_one_client(client_socket, msg):
    """Sends a message to a specific client."""
    try:
        client_socket.send(msg.encode('utf-8'))
    except Exception as e:
        print(f"Failed to deliver message. Error: {e}")


def send_to_all_clients(msg):
    """Broadcasts a message to all connected clients."""
    for user in connected_users:
        send_to_one_client(user[1], msg)


def remove_user(client_socket):
    """Removes a disconnected client."""
    global connected_users
    connected_users = [user for user in connected_users if user[1] != client_socket]
    client_socket.close()


def client_session(client_socket):
    """Handles the interaction with a newly connected client."""
    try:
        user_name = client_socket.recv(2048).decode('utf-8')
        if user_name:
            connected_users.append((user_name, client_socket))
            print(f"{user_name} joined.")
            send_to_all_clients(f"SERVER~{user_name} joined the chat!")
        else:
            print("Empty username received.")
            client_socket.close()
            return
    except Exception as e:
        print(f"Error in receiving username: {e}")
        client_socket.close()
        return

    threading.Thread(target=handle_messages, args=(client_socket, user_name)).start()


def start_server():
    """Main function to start the server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((SERVER_ADDRESS, SERVER_PORT))
        print(f"Server running at {SERVER_ADDRESS}:{SERVER_PORT}")
    except socket.error as e:
        print(f"Failed to bind server. Error: {e}")
        return

    server_socket.listen(MAX_CONNECTIONS)
    print("Waiting for clients to connect...")

    while True:
        try:
            client_socket, client_address = server_socket.accept()
            print(f"Connection established with {client_address}.")
            threading.Thread(target=client_session, args=(client_socket,)).start()
        except KeyboardInterrupt:
            print("Shutting down server.")
            for _, sock in connected_users:
                sock.close()
            server_socket.close()
            break


if __name__ == "__main__":
    start_server()
