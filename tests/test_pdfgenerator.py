# pylint: disable=redefined-outer-name
"""Tests for export """
import json
from unittest.mock import patch
import pytest
from falcon import testing
from service.resources.pdfgenerator import PDFGenerator
import service.microservice

CLIENT_HEADERS = {
    "ACCESS_KEY": "1234567"
}
CLIENT_ENV = {
    "ACCESS_KEY": CLIENT_HEADERS["ACCESS_KEY"],
    "SENDGRID_API_KEY": "abc",
}

@pytest.fixture()
def client():
    """ client fixture """
    return testing.TestClient(app=service.microservice.start_service())

@pytest.fixture
def mock_env(monkeypatch):
    """ mock environment access key """
    for key in CLIENT_ENV:
        monkeypatch.setenv(key, CLIENT_ENV[key])

def test_pdfgenerator(client, mock_env):
    # pylint: disable=unused-argument
    # mock_env is a fixture and creates a false positive for pylint
    """Test export message response"""


def test_pdfgenerator_exception(client, mock_env):
    # pylint: disable=unused-argument
    # mock_env is a fixture and creates a false positive for pylint
    """Test pdfgenerator exception """
