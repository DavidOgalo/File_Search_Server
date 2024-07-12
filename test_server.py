import pytest
import socket
import threading
import ssl
import time
from server import FileSearchServer

# Mock configurations for testing
class MockConfig:
    def __init__(self, path='./mock_file.txt', reread=True, ssl=True):
        self.linuxpath = path
        self.reread_on_query = reread
        self.ssl_enabled = ssl
        self.host = 'localhost'
        self.port = 12345

@pytest.fixture
def server(tmp_path):
    """Fixture to set up and tear down the server for testing."""
    # Create a temporary test file
    test_file = tmp_path / 'mock_file.txt'
    test_file.write_text('teststring\nexample\nanotherline\n')

    config = MockConfig(path=str(test_file))
    server = FileSearchServer(host=config.host, port=config.port)
    server.linuxpath = config.linuxpath
    server.reread_on_query = config.reread_on_query
    server.ssl_enabled = config.ssl_enabled
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    time.sleep(1)  # Give the server a moment to start
    yield server
    server.server_socket.close()

@pytest.fixture
def client():
    """Fixture to set up and tear down the client for testing."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12345))
    yield client_socket
    client_socket.close()

def ssl_wrap_socket(sock):
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    wrapped_socket = context.wrap_socket(sock, server_hostname='localhost')
    return wrapped_socket

def test_non_existent_query(server, client):
    try:
        wrapped_client = ssl_wrap_socket(client)
        wrapped_client.sendall(b'non_existent_query')
        response = wrapped_client.recv(1024).decode('utf-8')
        assert response.strip() == 'STRING NOT FOUND'
    except (ConnectionError, BrokenPipeError) as e:
        pytest.fail(f"Connection error occurred: {e}")
    finally:
        client.close()  # Ensure client connection is closed

def test_string_not_found(server, client):
    try:
        wrapped_client = ssl_wrap_socket(client)
        wrapped_client.sendall(b'1234abcd')
        response = wrapped_client.recv(1024).decode('utf-8')
        assert response.strip() == 'STRING NOT FOUND'
    except (ConnectionError, BrokenPipeError) as e:
        pytest.fail(f"Connection error occurred: {e}")
    finally:
        client.close()  # Ensure client connection is closed

def test_string_exists(server, client):
    try:
        wrapped_client = ssl_wrap_socket(client)
        wrapped_client.sendall(b'5;0;1;26;0;8;4;0;')
        response = wrapped_client.recv(1024).decode('utf-8')
        assert response.strip() == 'STRING EXISTS'
    except (ConnectionError, BrokenPipeError) as e:
        pytest.fail(f"Connection error occurred: {e}")
    finally:
        client.close()  # Ensure client connection is closed

def test_file_not_found(server, client):
    try:
        # Modify server's linuxpath to a non-existent file
        server.linuxpath = '/path/to/non_existent_file.txt'
        wrapped_client = ssl_wrap_socket(client)
        wrapped_client.sendall(b'teststring\n')
        response = wrapped_client.recv(1024).decode('utf-8')
        assert response.strip() == 'STRING NOT FOUND'
    except (ConnectionError, BrokenPipeError) as e:
        pytest.fail(f"Connection error occurred: {e}")
    finally:
        client.close()

def test_internal_server_error(server, client):
    try:
        # Trigger an internal server error by setting linuxpath to an invalid path
        server.linuxpath = '/invalid/path/to/file.txt'
        wrapped_client = ssl_wrap_socket(client)
        wrapped_client.sendall(b'teststring\n')
        response = wrapped_client.recv(1024).decode('utf-8')
        assert response.strip() == 'ERROR: Internal server error'
    except (ConnectionError, BrokenPipeError) as e:
        pytest.fail(f"Connection error occurred: {e}")
    finally:
        client.close()

def test_ssl_error(server, client):
    try:
        # Modify client to connect without SSL to trigger SSL error
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 12345))
        client_socket.sendall(b'teststring\n')
        response = client_socket.recv(1024).decode('utf-8')
        assert response.strip() == 'ERROR: SSL error'
    except ConnectionResetError as e:
        pytest.fail(f"Connection error occurred: {e}")
    finally:
        client_socket.close()

def test_empty_query(server, client):
    try:
        wrapped_client = ssl_wrap_socket(client)
        wrapped_client.sendall(b'')  # Send an empty query
        response = wrapped_client.recv(1024).decode('utf-8')
        assert response.strip() == 'ERROR: Empty query'
    except (ConnectionError, BrokenPipeError) as e:
        pytest.fail(f"Connection error occurred: {e}")
    finally:
        wrapped_client.close()  # Close the wrapped client socket
        client.close()  # Ensure client connection is closed

def test_payload_too_large(server, client):
    try:
        wrapped_client = ssl_wrap_socket(client)
        payload_size = 2048  # Set payload size larger than server's BUFFER_SIZE
        large_query = 'A' * payload_size
        wrapped_client.sendall(large_query.encode('utf-8'))
        response = wrapped_client.recv(1024).decode('utf-8')
        assert response.strip() == 'ERROR: Payload too large'
    except (ConnectionError, BrokenPipeError) as e:
        pytest.fail(f"Connection error occurred: {e}")
    finally:
        client.close()  # Ensure client connection is closed

if __name__ == '__main__':
    pytest.main()
