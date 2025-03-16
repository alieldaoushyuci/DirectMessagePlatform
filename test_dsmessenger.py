import pytest
import json
from ds_protocol import create_join_message, extract_json, extract_dm
from ds_messenger import DirectMessenger, DirectMessage
from unittest.mock import patch, MagicMock, mock_open
import socket
import time
import io

if __name__ == "__main__":
    pytest.main()

# Test for DirectMessage class initialization
def test_direct_message_init():
    dm = DirectMessage()
    assert dm.recipient is None
    assert dm.sender is None
    assert dm.message is None
    assert dm.timestamp is None

# Test for DirectMessenger initialization
def test_direct_messenger_init():
    messenger = DirectMessenger(dsuserver="example.com", username="user1", password="pass123")
    assert messenger.dsuserver == "example.com"
    assert messenger.username == "user1"
    assert messenger.password == "pass123"
    assert messenger.token is None

# Test for send method - success case
@patch("socket.socket")
def test_send_success(mock_socket):
    # Setup mock socket
    mock_socket_instance = MagicMock()
    mock_socket.return_value = mock_socket_instance
    
    # Setup mock fileobjects returned by makefile
    mock_send = MagicMock()
    mock_recv = MagicMock()
    
    # Configure mocks
    mock_socket_instance.makefile.side_effect = [mock_send, mock_recv]
    
    # Setup response data
    join_response = json.dumps({
        "response": {
            "type": "ok",
            "message": "Authentication successful",
            "token": "abc123"
        }
    })
    send_response = json.dumps({
        "response": {
            "type": "ok",
            "message": "Message sent"
        }
    })
    mock_recv.readline.side_effect = [join_response, send_response]
    
    # Create messenger and send message
    messenger = DirectMessenger(dsuserver="example.com", username="user1", password="pass123")
    result = messenger.send("Hello", "recipient1")
    
    # Assertions
    assert result is True
    assert messenger.token == "abc123"
    assert mock_socket_instance.connect.called
    assert mock_send.write.call_count == 2
    assert mock_send.flush.call_count == 2
    assert mock_recv.readline.call_count == 2

# Test for send method - error case
@patch("socket.socket")
def test_send_error(mock_socket):
    # Setup mock socket
    mock_socket_instance = MagicMock()
    mock_socket.return_value = mock_socket_instance
    
    # Setup mock fileobjects returned by makefile
    mock_send = MagicMock()
    mock_recv = MagicMock()
    
    # Configure mocks
    mock_socket_instance.makefile.side_effect = [mock_send, mock_recv]
    
    # Setup response data
    join_response = json.dumps({
        "response": {
            "type": "ok",
            "message": "Authentication successful",
            "token": "abc123"
        }
    })
    send_response = json.dumps({
        "response": {
            "type": "error",
            "message": "User not found"
        }
    })
    mock_recv.readline.side_effect = [join_response, send_response]
    
    # Create messenger and send message
    messenger = DirectMessenger(dsuserver="example.com", username="user1", password="pass123")
    result = messenger.send("Hello", "nonexistent_user")
    
    # Assertions
    assert result is False
    assert messenger.token == "abc123"
    assert mock_socket_instance.connect.called
    assert mock_send.write.call_count == 2
    assert mock_send.flush.call_count == 2
    assert mock_recv.readline.call_count == 2

# Test for send method with connection error
@patch("socket.socket")
def test_send_connection_error(mock_socket):
    # Setup mock socket to raise an exception on connect
    mock_socket_instance = MagicMock()
    mock_socket.return_value = mock_socket_instance
    mock_socket_instance.connect.side_effect = ConnectionError("Connection failed")
    
    # Create messenger and try to send message
    messenger = DirectMessenger(dsuserver="example.com", username="user1", password="pass123")
    
    # Test exception handling
    try:
        result = messenger.send("Hello", "recipient1")
        assert False, "Expected ConnectionError was not raised"
    except ConnectionError:
        pass  # This is the expected behavior if your code doesn't handle this exception

# Test for retrieve_new method - success case
@patch("socket.socket")
def test_retrieve_new_success(mock_socket):
    # Setup mock socket
    mock_socket_instance = MagicMock()
    mock_socket.return_value = mock_socket_instance
    
    # Setup mock fileobjects returned by makefile
    mock_send = MagicMock()
    mock_recv = MagicMock()
    
    # Configure mocks
    mock_socket_instance.makefile.side_effect = [mock_send, mock_recv]
    
    # Setup response data
    join_response = json.dumps({
        "response": {
            "type": "ok",
            "message": "Authentication successful",
            "token": "abc123"
        }
    })
    messages_response = json.dumps({
        "response": {
            "type": "ok",
            "messages": [
                {"from": "user2", "message": "Hi there", "timestamp": "123456"},
                {"from": "user3", "message": "Hello!", "timestamp": "123457"}
            ]
        }
    })
    mock_recv.readline.side_effect = [join_response, messages_response]
    
    # Create messenger and retrieve messages
    messenger = DirectMessenger(dsuserver="example.com", username="user1", password="pass123")
    messages = messenger.retrieve_new()
    
    # Assertions
    assert len(messages) == 2
    assert messages[0].sender == "user2"
    assert messages[0].message == "Hi there"
    assert messages[0].timestamp == "123456"
    assert messages[1].sender == "user3"
    assert messages[1].message == "Hello!"
    assert messages[1].timestamp == "123457"
    assert mock_socket_instance.connect.called
    assert mock_send.write.call_count == 2
    assert mock_send.flush.call_count == 2
    assert mock_recv.readline.call_count == 2

# Test for retrieve_new method - error case
@patch("socket.socket")
def test_retrieve_new_error(mock_socket):
    # Setup mock socket to raise an exception
    mock_socket_instance = MagicMock()
    mock_socket.return_value = mock_socket_instance
    mock_socket_instance.connect.side_effect = Exception("Test exception")
    
    # Create messenger and retrieve messages
    messenger = DirectMessenger(dsuserver="example.com", username="user1", password="pass123")
    messages = messenger.retrieve_new()
    
    # Should return None or empty list due to exception
    assert messages is None

# Test for retrieve_all method - success case
@patch("socket.socket")
@patch("builtins.open", new_callable=mock_open, read_data="")
@patch("ds_messenger.Profile")
@patch("pathlib.Path")
def test_retrieve_all_success(mock_path, mock_profile_class, mock_file, mock_socket):
    # Setup mock Profile
    mock_profile = MagicMock()
    mock_profile_class.return_value = mock_profile
    mock_profile.messages = []
    
    # Setup mock socket
    mock_socket_instance = MagicMock()
    mock_socket.return_value = mock_socket_instance
    
    # Setup mock fileobjects returned by makefile
    mock_send = MagicMock()
    mock_recv = MagicMock()
    
    # Configure mocks
    mock_socket_instance.makefile.side_effect = [mock_send, mock_recv]
    
    # Setup response data
    join_response = json.dumps({
        "response": {
            "type": "ok",
            "message": "Authentication successful",
            "token": "abc123"
        }
    })
    messages_response = json.dumps({
        "response": {
            "type": "ok",
            "messages": [
                {"from": "user2", "message": "Hi there", "timestamp": "123456"},
                {"recipient": "user2", "message": "Hello!", "timestamp": "123457"}
            ]
        }
    })
    mock_recv.readline.side_effect = [join_response, messages_response]
    
    # Create messenger and retrieve messages
    messenger = DirectMessenger(dsuserver="example.com", username="user1", password="pass123")
    messages = messenger.retrieve_all()
    
    # Assertions
    assert len(messages) == 2
    assert messages[0].sender == "user2"
    assert messages[0].message == "Hi there"
    assert messages[0].timestamp == "123456"
    assert messages[1].recipient == "user2"
    assert messages[1].message == "Hello!"
    assert messages[1].timestamp == "123457"
    assert mock_socket_instance.connect.called
    assert mock_send.write.call_count == 2
    assert mock_send.flush.call_count == 2
    assert mock_recv.readline.call_count == 2
    assert mock_profile.save_profile.call_count == 2

# Test for retrieve_all method - error case
@patch("socket.socket")
def test_retrieve_all_error(mock_socket):
    # Setup mock socket to raise an exception
    mock_socket_instance = MagicMock()
    mock_socket.return_value = mock_socket_instance
    mock_socket_instance.connect.side_effect = Exception("Test exception")
    
    # Create messenger and retrieve messages
    messenger = DirectMessenger(dsuserver="example.com", username="user1", password="pass123")
    messages = messenger.retrieve_all()
    
    # Should return None due to exception
    assert messages is None

# Test for retrieve_new with empty messages
@patch("socket.socket")
def test_retrieve_new_empty(mock_socket):
    # Setup mock socket
    mock_socket_instance = MagicMock()
    mock_socket.return_value = mock_socket_instance
    
    # Setup mock fileobjects returned by makefile
    mock_send = MagicMock()
    mock_recv = MagicMock()
    
    # Configure mocks
    mock_socket_instance.makefile.side_effect = [mock_send, mock_recv]
    
    # Setup response data
    join_response = json.dumps({
        "response": {
            "type": "ok",
            "message": "Authentication successful",
            "token": "abc123"
        }
    })
    messages_response = json.dumps({
        "response": {
            "type": "ok",
            "messages": []
        }
    })
    mock_recv.readline.side_effect = [join_response, messages_response]
    
    # Create messenger and retrieve messages
    messenger = DirectMessenger(dsuserver="example.com", username="user1", password="pass123")
    messages = messenger.retrieve_new()
    
    # Assertions
    assert isinstance(messages, list)
    assert len(messages) == 0
    assert mock_socket_instance.connect.called
    assert mock_send.write.call_count == 2
    assert mock_send.flush.call_count == 2
    assert mock_recv.readline.call_count == 2

# Test for failure in extract_dm during send
@patch("socket.socket")
@patch("ds_messenger.extract_dm")
def test_send_extract_failure(mock_extract_dm, mock_socket):
    # Setup mock socket
    mock_socket_instance = MagicMock()
    mock_socket.return_value = mock_socket_instance
    
    # Setup mock fileobjects returned by makefile
    mock_send = MagicMock()
    mock_recv = MagicMock()
    
    # Configure mocks
    mock_socket_instance.makefile.side_effect = [mock_send, mock_recv]
    mock_recv.readline.return_value = "dummy response"
    
    # Make extract_dm function fail
    mock_extract_dm.side_effect = [{"token": "abc123"}, {"type": "error"}]
    
    # Create messenger and send message
    messenger = DirectMessenger(dsuserver="example.com", username="user1", password="pass123")
    result = messenger.send("Hello", "recipient1")
    
    # Assertions
    assert result is False
    assert messenger.token == "abc123"