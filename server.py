import socket
import threading
import pickle
import os

# The server's IP and port
HOST = socket.gethostbyname(socket.gethostname())
PORT = 1235
SERVER_ADDRESS = (HOST, PORT)

# Header of the data transmitted indicating the length of the data.
# Before sending any data through the socket, a message with length HEADER_SIZE
# will be sent indicating the length of the incoming data
HEADER_SIZE = 8

# A disconnection message indicating the disconnecting of a client
# meaning closing the connection on the server-side
DISCONNECT_MESSAGE = "!DISCONNECT"

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] ESTABLISHED A NEW CONNECTION WITH {addr}, [ACTIVE CONNECTIONS] {threading.active_count() - 1}")

    def send_data(data):
        # In order for the data to be transmitted, it has to be in bytes format
        pickled_data = pickle.dumps(data)
        # Actual length of the data (for example 3) 
        data_length = len(pickled_data)
        # Padded length of the data (for example '3      ')
        padded_length = pickle.dumps(data_length)
        padded_length += b' ' * (HEADER_SIZE - len(padded_length))

        # Send the padded length and then the data right after
        conn.send(padded_length)
        conn.send(pickled_data)

    # An exception for client disconnection
    class ClientDisconnection(Exception): pass

    def receive_data():
        # Receive the first message (the header),
        # which indicates the incoming data length
        data_length = int(pickle.loads(conn.recv(HEADER_SIZE)))
        
        # Check the data is not None
        if data_length:
            # Receive the data itself
            data = pickle.loads(conn.recv(data_length))

            # Handle a client disconnection
            if data == DISCONNECT_MESSAGE:
                # Raise a disconnection error which will break the infint loop before sending back data
                raise ClientDisconnection
            else:
                # Print the incoming message
                print(f"[{addr[0], addr[1]}] {data}")

    try:
        while True:
            receive_data()
            send_data("MESSAGE APPROVED")
    except ClientDisconnection:
        print(f"[CLIENT DISCONNECTED] {addr} HAS DISCONNECTED")

    # Close the connection socket in case of a break caused by a disconnection
    conn.close()


def main():
    # Clear the terminal before a new run
    os.system('cls')    

    # Create the server_socket object and bind it to the desired address
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(SERVER_ADDRESS)
    
    # Start listening for new connections
    server_socket.listen()
    print(f"[LISTENING] SERVER IS NOW LISTENING FOR NEW CONNECTIONS ON {SERVER_ADDRESS}")

    while True:
        # Accept a new connection
        conn, addr = server_socket.accept()
        # Start a new thread handling the new connection
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()
        client_thread.join()

        # All clients have disconnected
        if threading.active_count() - 1 == 0:
            print("[SERVER DISCONNECTED] NO MORE CLIENTS LEFT")
            break
    
    server_socket.close()

if __name__ == "__main__":
    main()