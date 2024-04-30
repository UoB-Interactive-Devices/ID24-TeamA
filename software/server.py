import socket
import time
import random
import array
import sys
import _thread
import asyncio


# Define server IP address and port
SERVER_ADDRESS = ("192.168.137.1", 8080)

BUFFER_SIZE = 4096  # Adjust buffer size as needed
TIMEOUT_SECONDS = 5  # Adjust timeout value as needed

# Function to detect request
def detector(request):
    try:
        if request.decode()[0] == 'x':
            print(request.decode())
            return request.decode()
    except:
        pass

# Function to handle incoming HTTP requests
async def handle_request(client_sock):
    try:
        client_sock.settimeout(TIMEOUT_SECONDS)
        while True:
            request = await loop.sock_recv(client_sock, BUFFER_SIZE)
            if not request:
                break
            response = detector(request)
            split_response = response.split("/")
            # Respond with a simple "OK" message            
            if response[1] == 'C':
                name = split_response[1]
                print("Connected to: " + name)
            if response[1] == 'P':
                return
            if response[1] == 'R':
                return
            if response[1] == 'H':
                await loop.sock_sendall(client_sock, b"badum")
    except socket.timeout:
        print("Connection timed out")
    except Exception as e:
        print("An error occurred:", e)
    finally:
        client_sock.close()

# Main function
async def main():
    # Create a TCP/IP socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(SERVER_ADDRESS)
    server_sock.listen()

    print("Server is listening on", SERVER_ADDRESS)
    while True:
        client_sock, addr = await loop.sock_accept(server_sock)
        print("Connection from:", addr)
        asyncio.create_task(handle_request(client_sock))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())