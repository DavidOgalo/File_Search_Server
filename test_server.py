import pytest
import socket
import ssl
import configparser

# Load configuration settings
config = configparser.ConfigParser()
config.read('config.ini')

HOST = config.get('Server', 'host', fallback='localhost')
PORT = config.getint('Server', 'port', fallback=12345)
SSL_ENABLED = config.getboolean('Server', 'ssl_enabled', fallback=True)
BUFFER_SIZE = 1024  # Define a buffer size for payload tests

# Define helper function to send query to the server
def send_query(query):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if SSL_ENABLED:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            with context.wrap_socket(client_socket, server_hostname=HOST) as ssl_socket:
                ssl_socket.connect((HOST, PORT))
                ssl_socket.sendall(query.encode('utf-8'))
                response = ssl_socket.recv(BUFFER_SIZE).decode('utf-8')
        else:
            client_socket.connect((HOST, PORT))
            client_socket.sendall(query.encode('utf-8'))
            response = client_socket.recv(BUFFER_SIZE).decode('utf-8')
    finally:
        client_socket.close()
    return response

# Define the test cases
def test_empty_query():
    assert send_query('') == 'ERROR: Empty query'

def test_string_exists():
    assert send_query('existing_string') == 'STRING EXISTS'

def test_string_not_found():
    assert send_query('non_existing_string') == 'STRING NOT FOUND'

def test_payload_too_large():
    large_query = 'A' * (BUFFER_SIZE + 1)
    assert send_query(large_query) == 'ERROR: Payload too large'

def test_file_not_found():
    assert send_query('file_not_found') == 'ERROR: File not found'

def test_ssl_error_handling():
    with pytest.raises(ssl.SSLError):
        send_query('ssl_error')

# Main entry point to run the tests
if __name__ == '__main__':
    pytest.main()
