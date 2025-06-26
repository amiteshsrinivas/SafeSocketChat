"""Server Script for multithreaded chat application for two clients"""
from socket import *
from threading import Thread
import time
import sys

client_sock = []    # stores both client sockets
client_addresses = {}   # stores {key: client socket, values: client address}
public_keys = []     # stores public keys of both clients
active_connections = 0  # track number of active connections

def accept_incoming_connections():
    """Sets up handling for incoming clients"""
    global active_connections
    try:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        public_key = client.recv(BUFFER_SIZE)
        if not public_key:
            print("Failed to receive public key")
            return False
        client_sock.append(client)
        public_keys.append(public_key)
        client_addresses[client] = client_address
        active_connections += 1
        return True
    except Exception as e:
        print(f"Error accepting connection: {e}")
        return False

def handle_client1(client_sock, client_addresses):
    """Handles a first client connection"""
    try:
        if len(public_keys) < 2:
            print("Waiting for second client to connect...")
            return
            
        print("Sending public key to client 1")
        client_sock[0].send(public_keys[1])
        
        while True:
            try:
                msg = client_sock[0].recv(BUFFER_SIZE)
                if not msg:  # Client disconnected
                    print("Client 1 disconnected")
                    break
                if len(client_sock) > 1 and client_sock[1]:  # Check if second client is still connected
                    print("Forwarding message from client 1 to client 2")
                    client_sock[1].send(msg)
            except ConnectionResetError:
                print("Client 1 disconnected unexpectedly")
                break
            except Exception as e:
                print(f"Error in client 1 handler: {e}")
                break
    finally:
        cleanup_client(0)

def handle_client2(client_sock, client_addresses):
    """Handles a second client connection"""
    try:
        if len(public_keys) < 2:
            print("Waiting for first client to connect...")
            return
            
        print("Sending public key to client 2")
        client_sock[1].send(public_keys[0])
        
        while True:
            try:
                msg = client_sock[1].recv(BUFFER_SIZE)
                if not msg:  # Client disconnected
                    print("Client 2 disconnected")
                    break
                if len(client_sock) > 0 and client_sock[0]:  # Check if first client is still connected
                    print("Forwarding message from client 2 to client 1")
                    client_sock[0].send(msg)
            except ConnectionResetError:
                print("Client 2 disconnected unexpectedly")
                break
            except Exception as e:
                print(f"Error in client 2 handler: {e}")
                break
    finally:
        cleanup_client(1)

def cleanup_client(index):
    """Clean up resources when a client disconnects"""
    global active_connections
    try:
        if index < len(client_sock) and client_sock[index]:
            client_sock[index].close()
            if client_sock[index] in client_addresses:
                del client_addresses[client_sock[index]]
            client_sock[index] = None
            active_connections -= 1
            print(f"Cleaned up client {index}")
    except Exception as e:
        print(f"Error cleaning up client {index}: {e}")

#----SOCKET Part----
HOST = gethostbyname(gethostname())     # get host IP
PORT = 42000
BUFFER_SIZE = 4096   # increased buffer size for ECC keys and encrypted messages
ADDRESS = (HOST, PORT)  # servers socket address

try:
    SERVER = socket(AF_INET, SOCK_STREAM)   # create socket object
    SERVER.bind(ADDRESS)    # bind socket IP and port no.
    SERVER.listen(2)
    print('Server IP: ', HOST)
    print("Waiting for connection...")
    
    # Accept both clients first
    if accept_incoming_connections() and accept_incoming_connections():
        print("Both clients connected, starting message handlers")
        Thread(target=handle_client1, args=(client_sock, client_addresses)).start()
        Thread(target=handle_client2, args=(client_sock, client_addresses)).start()
        print('Encrypted conversation started')

        # Keep server running
        while True:
            if active_connections == 0:
                print("All clients disconnected. Shutting down server...")
                break
            time.sleep(1)

except KeyboardInterrupt:
    print("\nShutting down server...")
except Exception as e:
    print(f"Server error: {e}")
finally:
    # Clean up all resources
    for sock in client_sock:
        if sock:
            try:
                sock.close()
            except:
                pass
    SERVER.close()
    print("Server shutdown complete.")
