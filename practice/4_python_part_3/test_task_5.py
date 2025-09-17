import io
from unittest.mock import MagicMock, Mock, patch
import pytest
from urllib.error import HTTPError, URLError

from task_5 import make_request


def mock_response(code=200, body=b"OK"):
    response = MagicMock()
    response.code = code
    response.read.return_value = body

    cm = MagicMock()
    cm.__enter__.return_value = response
    cm.__exit__.return_value = False
    return cm


def test_make_request_success():
    mock_res = mock_response(200, b"Hello world")
    with patch("task_5.urlopen", return_value=mock_res):
        status, data = make_request("https://example.com")

    assert status == 200
    assert data == "Hello world"


def test_make_request_success_invalid_utf8():
    mock_res = mock_response(200, b"A\xffB")
    with patch("task_5.urlopen", return_value=mock_res):
        status, data = make_request("https://example.com")

    assert status == 200
    assert data == "A�B"    


def test_make_request_http_error():
    fp = io.BytesIO(b"not found")
    err = HTTPError(url="https://example.com", code=404, msg="Not Found", hdrs=None, fp=fp)
    with patch("task_5.urlopen", side_effect=err):
        status, data = make_request("https://example.com")

    assert status == 404
    assert data == "not found"


def test_make_request_url_error():
    with patch("task_5.urlopen", side_effect=URLError("dns failure")):
        status, data = make_request("https://example.com")

    assert status == 0
    assert "dns failure" in data
