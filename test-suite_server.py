import pytest
import socket
import threading
import ssl
import time
from server import FileSearchServer

# Mock configurations for testing environment


class MockConfig:
    def __init__(
        self, path: str = "./mock_file.txt", reread: bool = True, ssl: bool = True
    ) -> None:
        self.linuxpath = path
        self.reread_on_query = reread
        self.ssl_enabled = ssl
        self.host = "localhost"
        self.port = 0  # 0 means the OS will select an available port


@pytest.fixture
def server(tmp_path) -> FileSearchServer:  # type: ignore
    """Fixture to set up and tear down the server for testing."""
    test_file = tmp_path / "mock_file.txt"
    test_file.write_text("teststring\nexample\nanotherline\n")

    config = MockConfig(path=str(test_file))
    server = FileSearchServer(host=config.host, port=config.port)
    server.linuxpath = config.linuxpath
    server.reread_on_query = config.reread_on_query
    server.ssl_enabled = config.ssl_enabled

    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()

    # Allow time for server to start
    time.sleep(1)

    # Set the server port to the assigned port
    config.port = server.server_socket.getsockname()[1]

    yield server

    # Properly close and shutdown the server
    server.server_socket.close()
    server_thread.join(timeout=5)  # Allow time for the server thread to exit


@pytest.fixture
def client(server: FileSearchServer) -> socket.socket:  # type: ignore
    """Fixture to set up and tear down the client for testing."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(
        (server.server_socket.getsockname()[0], server.server_socket.getsockname()[1])
    )
    yield client_socket
    client_socket.close()


def ssl_wrap_socket(sock: socket.socket) -> ssl.SSLSocket:
    """Wrap the socket with SSL."""
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context.wrap_socket(sock, server_hostname="localhost")


def test_non_existent_query(server: FileSearchServer, client: socket.socket) -> None:
    """Test sending a non-existent query to the server."""
    try:
        wrapped_client = ssl_wrap_socket(client)
        wrapped_client.sendall(b"non_existent_query")
        response = wrapped_client.recv(1024).decode("utf-8")
        assert response.strip() == "STRING NOT FOUND"
    except (ConnectionError, BrokenPipeError, ssl.SSLError) as e:
        pytest.fail(f"SSL/Connection error occurred: {e}")


def test_string_not_found(server: FileSearchServer, client: socket.socket) -> None:
    """Test sending a query that does not match any string in the file."""
    try:
        wrapped_client = ssl_wrap_socket(client)
        wrapped_client.sendall(b"1234abcd")
        response = wrapped_client.recv(1024).decode("utf-8")
        assert response.strip() == "STRING NOT FOUND"
    except (ConnectionError, BrokenPipeError, ssl.SSLError) as e:
        pytest.fail(f"SSL/Connection error occurred: {e}")


def test_string_exists(server: FileSearchServer, client: socket.socket) -> None:
    """Test sending a query that matches a string in the file."""
    try:
        wrapped_client = ssl_wrap_socket(client)
        wrapped_client.sendall(b"6;0;1;26;0;7;3;0;\n")
        response = wrapped_client.recv(1024).decode("utf-8")
        assert response.strip() == "STRING EXISTS"
    except (ConnectionError, BrokenPipeError, ssl.SSLError) as e:
        pytest.fail(f"SSL/Connection error occurred: {e}")


def test_file_not_found(server: FileSearchServer, client: socket.socket) -> None:
    """Test server behavior when the file is not found."""
    try:
        server.linuxpath = "/path/to/non_existent_file.txt"
        wrapped_client = ssl_wrap_socket(client)
        wrapped_client.sendall(b"teststring\n")
        response = wrapped_client.recv(1024).decode("utf-8")
        assert response.strip() == "STRING NOT FOUND"
    except (ConnectionError, BrokenPipeError, ssl.SSLError) as e:
        pytest.fail(f"SSL/Connection error occurred: {e}")


def test_client_disconnection_handling(
    server: FileSearchServer, client: socket.socket
) -> None:
    """Test the server's handling of a client disconnection."""
    try:
        wrapped_client = ssl_wrap_socket(client)
        wrapped_client.sendall(b"teststring\n")
        wrapped_client.close()
        time.sleep(1)  # Allow time for the server to handle disconnection
    except (ConnectionError, BrokenPipeError, ssl.SSLError) as e:
        pytest.fail(f"SSL/Connection error occurred: {e}")


def test_multiple_concurrent_clients(server: FileSearchServer) -> None:
    """Test handling multiple concurrent clients."""
    num_clients = 5
    clients = []

    try:
        for _ in range(num_clients):
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(
                (
                    server.server_socket.getsockname()[0],
                    server.server_socket.getsockname()[1],
                )
            )
            clients.append(client_socket)

        threads = []
        for client_socket in clients:
            thread = threading.Thread(target=send_query, args=(client_socket,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
    except (ConnectionError, BrokenPipeError, ssl.SSLError) as e:
        pytest.fail(f"SSL/Connection error occurred: {e}")
    finally:
        for client_socket in clients:
            client_socket.close()


def send_query(client_socket: socket.socket) -> None:
    """Helper function to send a query from a client socket."""
    wrapped_client = ssl_wrap_socket(client_socket)
    wrapped_client.sendall(b"teststring\n")
    response = wrapped_client.recv(1024).decode("utf-8")
    assert response.strip() == "STRING NOT FOUND"


def test_query_timeout_handling(
    server: FileSearchServer, client: socket.socket
) -> None:
    """Test handling a query that triggers a timeout."""
    try:
        wrapped_client = ssl_wrap_socket(client)
        # Large query to cause timeout
        wrapped_client.sendall(b"B" * (1024 + 1))
        response = wrapped_client.recv(1024).decode("utf-8")
        assert response.strip() == "STRING NOT FOUND"
    except (ConnectionError, BrokenPipeError, ssl.SSLError) as e:
        pytest.fail(f"SSL/Connection error occurred: {e}")


if __name__ == "__main__":
    pytest.main()
