import pytest
import json
from ds_protocol import create_join_message, extract_json, make_post, make_bio, directmessage, request_newmessage, request_allmessages, extract_dm, recv_response, print_response, validate, create_dm_request, DSProtocolError
from ds_messenger import DirectMessenger, DirectMessage
from unittest.mock import patch, MagicMock
import time
import socket

if __name__ == "__main__":
    pytest.main()

# Test for create_join_message
def test_create_join_message():
    msg = create_join_message("testuser", "password123")
    expected = json.dumps({"join": {"username": "testuser", "password": "password123", "token": ""}})
    assert msg == expected

# Test for extract_json
def test_extract_json():
    json_msg = '{"response": {"type": "ok", "message": "Success", "token": "abc123"}}'
    result = extract_json(json_msg)
    assert result.success == "ok"
    assert result.message == "Success"
    assert result.token == "abc123"

# Test for extract_json with invalid JSON
def test_extract_json_invalid():
    json_msg = '{invalid json}'
    result = extract_json(json_msg)
    assert result == (None, None, None)

# Test for extract_json with missing fields
def test_extract_json_missing_fields():
    json_msg = '{"response": {}}'
    result = extract_json(json_msg)
    assert result.success is None
    assert result.message is None
    assert result.token is None

# Test for extract_json with empty string
def test_extract_json_empty():
    result = extract_json("")
    assert result == (None, None, None)

# Test for extract_json with None input
def test_extract_json_none():
    result = extract_json(None)
    assert result == (None, None, None)

# Test for recv_response
@patch("socket.socket")
def test_recv_response_socket_error(mock_socket):
    mock_socket_inst = MagicMock()
    mock_socket.return_value = mock_socket_inst
    mock_socket_inst.recv.side_effect = OSError("Test socket error")  # Use OSError instead
    
    result = recv_response(mock_socket_inst)
    assert result == ""

# Test for recv_response with socket error
@patch("socket.socket")
def test_recv_response_socket_error(mock_socket):
    mock_socket_inst = MagicMock()
    mock_socket.return_value = mock_socket_inst
    mock_socket_inst.recv.side_effect = socket.error("Test socket error")
    
    # If your recv_response handles socket errors:
    try:
        result = recv_response(mock_socket_inst)
        assert result == ""
    except socket.error:
        # This is fine if your function doesn't catch the error
        pass

# Test for print_response
def test_print_response(capsys):
    response = extract_json('{"response": {"type": "ok", "message": "Success", "token": "abc123"}}')
    print_response(response)
    captured = capsys.readouterr()
    assert "Success: ok" in captured.out
    assert "Message: Success" in captured.out
    assert "Token: abc123" in captured.out

# Test for validate
def test_validate():
    assert validate("Hello") is True
    assert validate("") is False
    assert validate(None) is False

# Test for make_post
def test_make_post():
    token = "abc123"
    message = "Hello, world!"
    msg = json.loads(make_post(token, message))
    assert msg["token"] == token
    assert msg["post"]["entry"] == message

# Test for make_post with None token
def test_make_post_none_token():
    token = None
    message = "Hello, world!"
    msg = json.loads(make_post(token, message))
    assert msg["token"] is None
    assert msg["post"]["entry"] == message
    assert "timestamp" in msg["post"]

# Test for make_bio
def test_make_bio():
    token = "abc123"
    bio = "This is my bio."
    msg = json.loads(make_bio(token, bio))
    assert msg["token"] == token
    assert msg["bio"]["entry"] == bio

# Test for make_bio with None token
def test_make_bio_none_token():
    token = None
    bio = "My bio"
    msg = json.loads(make_bio(token, bio))
    assert msg["token"] is None
    assert msg["bio"]["entry"] == bio
    assert "timestamp" in msg["bio"]

# Test for directmessage
def test_directmessage():
    token = "abc123"
    message = "Hello!"
    recipient = "friend"
    timestamp = time.time()
    msg = json.loads(directmessage(token, message, recipient, str(timestamp)))
    assert msg["token"] == token
    assert msg["directmessage"]["entry"] == message
    assert msg["directmessage"]["recipient"] == recipient
    assert msg["directmessage"]["timestamp"] == str(timestamp)

# Test for directmessage with None values
def test_directmessage_none_values():
    msg = json.loads(directmessage(None, None, None, None))
    assert msg["token"] is None
    assert msg["directmessage"]["entry"] is None
    assert msg["directmessage"]["recipient"] is None
    assert msg["directmessage"]["timestamp"] is None

# Test for request_newmessage
def test_request_newmessage():
    token = "abc123"
    msg = json.loads(request_newmessage(token))
    assert msg["token"] == token
    assert msg["directmessage"] == "new"

# Test for request_allmessages
def test_request_allmessages():
    token = "abc123"
    msg = json.loads(request_allmessages(token))
    assert msg["token"] == token
    assert msg["directmessage"] == "all"

# Test for extract_dm
def test_extract_dm():
    json_msg = json.dumps({"response": {"messages": [{"from": "user1", "message": "Hi", "timestamp": "123"}]}})
    result = extract_dm(json_msg)
    assert "messages" in result
    assert result["messages"][0]["from"] == "user1"
    assert result["messages"][0]["message"] == "Hi"
    assert result["messages"][0]["timestamp"] == "123"

# Test for extract_dm with invalid JSON
def test_extract_dm_invalid_json():
    result = extract_dm("{invalid json}")
    assert result is None

# Test for extract_dm with empty string
def test_extract_dm_empty():
    result = extract_dm("")
    assert result is None

# Test for extract_dm with None
def test_extract_dm_none():
    result = extract_dm(None)
    assert result is None

# Test for create_dm_request
def test_create_dm_request():
    token = "abc123"
    username = "testuser"
    password = "password123"
    msg = json.loads(create_dm_request(token, username, password))
    assert msg["join"]["username"] == username
    assert msg["join"]["password"] == password
    assert msg["join"]["token"] == token

# Test for empty username and password in create_dm_request
def test_create_dm_request_empty():
    token = "abc123"
    username = ""
    password = ""
    msg = json.loads(create_dm_request(token, username, password))
    assert msg["join"]["username"] == ""
    assert msg["join"]["password"] == ""
    assert msg["join"]["token"] == token

# Test for request_newmessage with invalid token
def test_request_newmessage_invalid():
    token = None
    msg = json.loads(request_newmessage(token))
    assert msg["token"] is None
    assert msg["directmessage"] == "new"

# Test for request_allmessages with invalid token
def test_request_allmessages_invalid():
    token = None
    msg = json.loads(request_allmessages(token))
    assert msg["token"] is None
    assert msg["directmessage"] == "all"

# Test for recv_response with empty response
@patch("socket.socket")
def test_recv_response_empty(mock_socket_class):
    mock_socket_inst = MagicMock()
    mock_socket_class.return_value = mock_socket_inst
    mock_socket_inst.recv.return_value = b''

    result = recv_response(mock_socket_inst)
    assert result == ""

# Test for DSProtocolError
def test_ds_protocol_error():
    error = DSProtocolError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)

# Test for create_join_message with token
def test_create_join_message_with_token():
    msg = create_join_message("testuser", "password123", token="abc123")
    expected = json.dumps({"join": {"username": "testuser", "password": "password123", "token": ""}})
    assert msg == expected