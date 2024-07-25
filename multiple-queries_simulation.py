import socket
import ssl
import time
import threading
import configparser
from typing import Optional

# Read configuration settings
config = configparser.ConfigParser()
config.read("config.ini")

HOST: str = config.get("Server", "host", fallback="localhost")
PORT: int = config.getint("Server", "port", fallback=12345)
SSL_ENABLED: bool = config.getboolean("Server", "ssl_enabled", fallback=True)
NUM_CLIENTS: int = 50  # Number of clients to simulate
QUERY_STRING: str = "11;0;23;11;0;20;5;0;"  # Example query string
BUFFER_SIZE: int = 1024  # Buffer size for receiving data


def client_task(query: str) -> None:
    """
    Task for each client thread to send a query to the server.

    Args:
        query: The query string to send to the server.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        if SSL_ENABLED:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            with context.wrap_socket(client_socket, server_hostname=HOST) as ssl_socket:
                ssl_socket.connect((HOST, PORT))
                ssl_socket.sendall(query.encode("utf-8"))
                response = ssl_socket.recv(BUFFER_SIZE).decode("utf-8")
                print(f"Server response: {response}")
        else:
            client_socket.connect((HOST, PORT))
            client_socket.sendall(query.encode("utf-8"))
            response = client_socket.recv(BUFFER_SIZE).decode("utf-8")
            print(f"Server response: {response}")
    except Exception as e:
        print(f"Exception occurred: {e}")
    finally:
        client_socket.close()


def test_performance() -> None:
    """
    Run the performance test with multiple concurrent clients.
    """
    threads = []
    start_time = time.time()

    for _ in range(NUM_CLIENTS):
        thread = threading.Thread(target=client_task, args=(QUERY_STRING,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    end_time = time.time()
    print(
        f"Total execution time for {NUM_CLIENTS} clients: {end_time - start_time:.4f} seconds"
    )


if __name__ == "__main__":
    test_performance()
