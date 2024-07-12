import socket
import threading
import configparser
import ssl
import logging

# Load configuration settings
config = configparser.ConfigParser()
config.read('config.ini')

# Get the path to the file and the REREAD_ON_QUERY option with default values
linuxpath = config.get('Settings', 'linuxpath', fallback='./200k.txt')
reread_on_query = config.getboolean('Settings', 'REREAD_ON_QUERY', fallback=True)

# Get server host and port from the configuration
HOST = 'localhost'  # Default value for the server host
PORT = 12345  # Default value for the server port
SSL_ENABLED = True  # Default value to enable SSL
BUFFER_SIZE = 1024  # Default buffer size

# Check if 'Server' section exists in the config file
if 'Server' in config:
    HOST = config.get('Server', 'host', fallback=HOST)
    PORT = config.getint('Server', 'port', fallback=PORT)
    SSL_ENABLED = config.getboolean('Server', 'ssl_enabled', fallback=SSL_ENABLED)
    BUFFER_SIZE = config.getint('Server', 'buffer_size', fallback=BUFFER_SIZE)

# Set up logging to track server activity
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class FileSearchServer:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.server_socket = None
        self.ssl_context = None

    def setup_server(self):
        # Create a TCP/IP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logger.info(f'Server listening on {self.host}:{self.port}')

        if SSL_ENABLED:
            # Set up SSL context if SSL is enabled
            self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self.ssl_context.load_cert_chain(certfile='server.crt', keyfile='server.key')
            logger.info('SSL enabled: Using SSL for secure connections')
        else:
            logger.info('SSL not enabled: Using plain TCP connections')

    def handle_client(self, client_socket):
        # Handle client connections
        try:
            if self.ssl_context:
                with self.ssl_context.wrap_socket(client_socket, server_side=True) as ssl_socket:
                    self.process_request(ssl_socket)
            else:
                self.process_request(client_socket)
        except ssl.SSLError as e:
            logger.error(f'SSL error: {e}')
            # Handle SSL errors without interacting with the client socket
        except Exception as e:
            logger.error(f'Error handling client: {e}')
            # Handle other exceptions without interacting with the client socket
        finally:
            client_socket.close()

    def process_request(self, socket):
        try:
            data = socket.recv(BUFFER_SIZE).decode('utf-8')
            logger.info(f'Received query: {data}')
            
            if len(data) > BUFFER_SIZE:
                socket.sendall('ERROR: Payload too large'.encode('utf-8'))
                return

            if not data.strip():  # Check for empty query
                socket.sendall('ERROR: Empty query'.encode('utf-8'))
                return

            response = self.process_query(data)
            socket.sendall(response.encode('utf-8'))
        except Exception as e:
            logger.error(f'Error processing request: {e}')
            socket.sendall('ERROR: Internal server error'.encode('utf-8'))

    def process_query(self, query):
        try:
            if reread_on_query:
                with open(linuxpath, 'r') as file:
                    data = file.readlines()
            else:
                if not hasattr(self, 'data'):
                    with open(linuxpath, 'r') as file:
                        self.data = file.readlines()
                data = self.data

            query = query.strip()  # Remove any leading or trailing whitespace from the query
            results = [line.strip() for line in data if query == line.strip()]  # Check for exact matches

            if results:
                return 'STRING EXISTS'
            else:
                return 'STRING NOT FOUND'
        except FileNotFoundError:
            logger.error(f'File not found: {linuxpath}')
            return 'STRING NOT FOUND'
        except Exception as e:
            logger.error(f'Error processing query: {e}')
            return 'ERROR: Internal server error'

    def start(self):
        # Start the server and handle clients
        self.setup_server()
        while True:
            try:
                client_socket, client_address = self.server_socket.accept()
                logger.info(f'Connection from {client_address}')
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()
            except Exception as e:
                logger.error(f'Error accepting connections: {e}')
                break

if __name__ == '__main__':
    server = FileSearchServer()
    server.start()
