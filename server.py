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
HOST = config.get('Server', 'host', fallback='localhost')
PORT = config.getint('Server', 'port', fallback=12345)
SSL_ENABLED = config.getboolean('Server', 'ssl_enabled', fallback=True)

# Set up logging to track server activity
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class FileSearchServer:
    def handle_client(conn, addr):
        """Handles incoming client connections."""
        logging.info(f'Connected by {addr}')
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                query = data.decode('utf-8')
                logging.info(f'Received query: {query}')
                result = process_query(query)
                conn.sendall(result.encode('utf-8'))
        logging.info(f'Connection with {addr} closed')


    def process_query(query):
        """Process the query received from the client."""
        return f'Search result for query: {query}'

    def start():
        """Main function to set up and start the server."""
        context = None
        if SSL_ENABLED:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile='server.crt', keyfile='server.key')

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            logging.info(f'Server listening on {HOST}:{PORT}')
            while True:
                conn, addr = s.accept()
                if SSL_ENABLED:
                    conn = context.wrap_socket(conn, server_side=True)
                threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == '__main__':
    server = FileSearchServer()
    server.start()
