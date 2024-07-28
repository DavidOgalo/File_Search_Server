import socket
import threading
import configparser
import ssl
import logging
import time
from typing import List, Optional

# Load configuration settings
config = configparser.ConfigParser()
config.read("config.ini")

# Get the path to the file and the REREAD_ON_QUERY option with default values
linuxpath = config.get("Settings", "linuxpath", fallback="./200k.txt")
reread_on_query = config.getboolean("Settings", "REREAD_ON_QUERY", fallback=True)

# Get server host and port from the configuration
HOST = config.get("Server", "host", fallback="localhost")
PORT = config.getint("Server", "port", fallback=12345)
SSL_ENABLED = config.getboolean("Server", "ssl_enabled", fallback=True)
BUFFER_SIZE = config.getint("Server", "buffer_size", fallback=1024)

# Set up logging to track server activity
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()


class FileSearchServer:
    def __init__(self, host: str = HOST, port: int = PORT):
        """
        Initialize the FileSearchServer.

        :param host: Host address to bind the server.
        :param port: Port number to bind the server.
        """
        self.host = host
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.ssl_context: Optional[ssl.SSLContext] = None

    def setup_server(self) -> None:
        """Set up the server socket and SSL context if enabled."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logger.info("Server listening on %s:%d", self.host, self.port)

        if SSL_ENABLED:
            self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self.ssl_context.load_cert_chain(
                certfile="server.crt", keyfile="server.key"
            )
            logger.info("SSL enabled: Using SSL for secure connections")
        else:
            logger.info("SSL not enabled: Using plain TCP connections")

    def handle_client(self, client_socket: socket.socket) -> None:
        """Handle client connections."""
        try:
            if self.ssl_context:
                with self.ssl_context.wrap_socket(
                    client_socket, server_side=True
                ) as ssl_socket:
                    self.process_request(ssl_socket)
            else:
                self.process_request(client_socket)
        except ssl.SSLError as e:
            logger.error("SSL error: %s", e)
        except Exception as e:
            logger.error("Error handling client: %s", e)
        finally:
            client_socket.close()

    def process_request(self, client_socket: socket.socket) -> None:
        """Process a request from the client."""
        try:
            start_time = time.time()
            data = client_socket.recv(BUFFER_SIZE).decode("utf-8")
            logger.info("Received query: %s", data)

            if len(data) > BUFFER_SIZE:
                client_socket.sendall("ERROR: Payload too large".encode("utf-8"))
                return

            if not data.strip():
                client_socket.sendall("ERROR: Empty query".encode("utf-8"))
                return

            response = self.process_query(data)
            client_socket.sendall(response.encode("utf-8"))
            execution_time = time.time() - start_time
            logger.info("Processed request in %.2f seconds", execution_time)
        except Exception as e:
            logger.error("Error processing request: %s", e)
            client_socket.sendall("ERROR: Internal server error".encode("utf-8"))

    def process_query(self, query: str) -> str:
        """
        Process the search query.

        :param query: The query string to search for in the file.
        :return: The result of the search.
        """
        try:
            if reread_on_query:
                with open(linuxpath, "r") as file:
                    data = file.readlines()
            else:
                if not hasattr(self, "data"):
                    with open(linuxpath, "r") as file:
                        self.data = file.readlines()
                data = self.data

            query = query.strip()
            results = [line.strip() for line in data if query == line.strip()]

            return "STRING EXISTS" if results else "STRING NOT FOUND"
        except FileNotFoundError:
            logger.error("File not found: %s", linuxpath)
            return "STRING NOT FOUND"
        except Exception as e:
            logger.error("Error processing query: %s", e)
            return "ERROR: Internal server error"

    def start(self) -> None:
        """Start the server and handle clients."""
        self.setup_server()
        while True:
            try:
                if (
                    self.server_socket is not None
                ):  # Add a check to ensure server_socket is not None
                    client_socket, client_address = self.server_socket.accept()
                    logger.info("Connection from %s", client_address)
                    client_thread = threading.Thread(
                        target=self.handle_client, args=(client_socket,)
                    )
                    client_thread.start()
                else:
                    logger.error("Server socket is not initialized.")
                    break
            except Exception as e:
                logger.error("Error accepting connections: %s", e)
                break


if __name__ == "__main__":
    server = FileSearchServer()
    server.start()
