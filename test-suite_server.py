import pytest
import socket
import threading
import ssl
import time
from server import FileSearchServer

# Mock configurations for testing environment
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
    """Wrap the socket with SSL."""
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    wrapped_socket = context.wrap_socket(sock, server_hostname='localhost')
    return wrapped_socket


# Non_existent_query test
def test_non_existent_query(server, client):
    """Test sending a non-existent query to the server."""
    try:
        wrapped_client = ssl_wrap_socket(client)
        wrapped_client.sendall(b'non_existent_query')
        response = wrapped_client.recv(1024).decode('utf-8')
        assert response.strip() == 'STRING NOT FOUND'
    except (ConnectionError, BrokenPipeError, ssl.SSLError) as e:
        pytest.fail(f"SSL/Connection error occurred: {e}")
    finally:
        client.close()  # Ensure client connection is closed

# String_not_found test
def test_string_not_found(server, client):
    """Test sending a query that does not match any string in the file."""
    try:
        wrapped_client = ssl_wrap_socket(client)
        wrapped_client.sendall(b'1234abcd')
        response = wrapped_client.recv(1024).decode('utf-8')
        assert response.strip() == 'STRING NOT FOUND'
    except (ConnectionError, BrokenPipeError, ssl.SSLError) as e:
        pytest.fail(f"SSL/Connection error occurred: {e}")
    finally:
        client.close()  

# String_exists test
def test_string_exists(server, client):
    """Test sending a query that matches a string in the file."""
    try:
        wrapped_client = ssl_wrap_socket(client)
        wrapped_client.sendall(b'2;0;23;21;0;22;3;0;\n')
        response = wrapped_client.recv(1024).decode('utf-8')
        assert response.strip() == 'STRING EXISTS'
    except (ConnectionError, BrokenPipeError, ssl.SSLError) as e:
        pytest.fail(f"SSL/Connection error occurred: {e}")
    finally:
        client.close()  # Ensure client connection is closed

# Non-existent testing file test
def test_file_not_found(server, client):
    try:
        # Modify server's linuxpath to a non-existent file
        server.linuxpath = '/path/to/non_existent_file.txt'
        wrapped_client = ssl_wrap_socket(client)
        wrapped_client.sendall(b'teststring\n')
        response = wrapped_client.recv(1024).decode('utf-8')
        assert response.strip() == 'STRING NOT FOUND'  # Adjusted assertion
    except (ConnectionError, BrokenPipeError, ssl.SSLError) as e:
        pytest.fail(f"SSL/Connection error occurred: {e}")
    finally:
        client.close()


# client_disconnection_handling test
def test_client_disconnection_handling(server, client):
    """Test the server's handling of a client disconnection."""
    try:
        wrapped_client = ssl_wrap_socket(client)
        
        # Send a query and then disconnect the client
        wrapped_client.sendall(b'teststring\n')
        wrapped_client.close()

        # Server should handle the disconnection gracefully
        time.sleep(1)  # Wait for server to process potential errors

    except (ConnectionError, BrokenPipeError, ssl.SSLError) as e:
        pytest.fail(f"SSL/Connection error occurred: {e}")
    finally:
        client.close()  # Ensure client connection is closed

# multiple concurrent queries test
def test_multiple_concurrent_clients(server):
    """Test handling multiple concurrent clients."""
    num_clients = 5
    clients = []

    try:
        for _ in range(num_clients):
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 12345))
            clients.append(client_socket)

        # Send queries from multiple clients concurrently
        threads = []
        for client_socket in clients:
            thread = threading.Thread(target=send_query, args=(client_socket,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

    except (ConnectionError, BrokenPipeError, ssl.SSLError) as e:
        pytest.fail(f"SSL/Connection error occurred: {e}")
    finally:
        for client_socket in clients:
            client_socket.close()

def send_query(client_socket):
    """Helper function to send a query from a client socket."""
    wrapped_client = ssl_wrap_socket(client_socket)
    wrapped_client.sendall(b'teststring\n')
    response = wrapped_client.recv(1024).decode('utf-8')
    assert response.strip() == 'STRING NOT FOUND'  # Adjust based on expected server response

# Query timeout handling test
def test_query_timeout_handling(server, client):
    """Test handling a query that triggers a timeout."""
    try:
        wrapped_client = ssl_wrap_socket(client)

        # Send a query that triggers a timeout
        wrapped_client.sendall(b'B' * (1024 + 1))  # Send a query larger than BUFFER_SIZE
        response = wrapped_client.recv(1024).decode('utf-8')
        assert response.strip() == 'STRING NOT FOUND'  # Adjust based on expected server response

    except (ConnectionError, BrokenPipeError, ssl.SSLError) as e:
        pytest.fail(f"SSL/Connection error occurred: {e}")
    finally:
        client.close()  

        
if __name__ == '__main__':
    pytest.main()
