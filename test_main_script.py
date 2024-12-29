import unittest
from unittest.mock import patch, MagicMock
from unittest.mock import ANY
import os
import base64
from io import StringIO

# Tests

# Import functions from the main script
from jira_cli_tool import (
    encode_base64,
    decode_base64,
    save_config,
    load_config,
    get_headers,
    get_issue,
    create_issue,
    update_issue,
    list_issues,
    delete_issue,
)

class TestJiraCLITool(unittest.TestCase):
    CONFIG_FILE = "test_config.ini"

    @classmethod
    def setUpClass(cls):
        """Set up any global test configuration."""
        # Mock the config file to avoid overwriting the real one
        global CONFIG_FILE
        CONFIG_FILE = cls.CONFIG_FILE

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        if os.path.exists(cls.CONFIG_FILE):
            os.remove(cls.CONFIG_FILE)

    def test_encode_decode_base64(self):
        """Test Base64 encoding and decoding."""
        original = "test_string"
        encoded = encode_base64(original)
        decoded = decode_base64(encoded)
        self.assertEqual(decoded, original, "Decoded value should match the original")

    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        save_config("https://test.atlassian.net", "test_email", "test_token")
        config = load_config()
        self.assertEqual(config["base_url"], "https://test.atlassian.net")
        self.assertEqual(config["email"], "test_email")
        self.assertEqual(config["api_token"], "test_token")

    def test_get_headers(self):
        """Test HTTP header generation."""
        headers = get_headers("test_email", "test_token")
        expected_auth = f"Basic {base64.b64encode('test_email:test_token'.encode()).decode()}"
        self.assertEqual(headers["Authorization"], expected_auth)
        self.assertEqual(headers["Content-Type"], "application/json")

    @patch("requests.get")
    @patch("jira_cli_tool.load_config",
           return_value={"base_url": "https://test.atlassian.net", "email": "test_email", "api_token": "test_token"})
    @patch("sys.stdout", new_callable=StringIO)
    def test_get_issue(self, mock_stdout, mock_load_config, mock_get):
        """Test fetching an issue."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "key": "TEST-1",
            "fields": {"summary": "Test Issue", "status": {"name": "To Do"}}
        }
        mock_get.return_value = mock_response

        with patch("builtins.input", side_effect=["TEST-1"]):
            get_issue()

        # Retrieve the base_url from the mocked configuration
        base_url = mock_load_config.return_value["base_url"]
        expected_url = f"{base_url}/rest/api/3/issue/TEST-1"

        # Assert the correct URL was used in the GET request
        mock_get.assert_called_once_with(expected_url, headers=ANY)

        # Assert that the correct output was printed
        output = mock_stdout.getvalue()
        self.assertIn(f"Fetching issue from URL: {expected_url}", output)
        self.assertIn("Issue Details:", output)
        self.assertIn("Key: TEST-1", output)
        self.assertIn("Summary: Test Issue", output)
        self.assertIn("Status: To Do", output)

    @patch("requests.post")
    def test_create_issue(self, mock_post):
        """Test creating an issue."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"key": "TEST-1"}
        mock_post.return_value = mock_response

        with patch("builtins.input", side_effect=["TEST", "Test Summary", "Task"]):
            create_issue()

        mock_post.assert_called_once()

    @patch("requests.put")
    def test_update_issue(self, mock_put):
        """Test updating an issue."""
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_put.return_value = mock_response

        with patch("builtins.input", side_effect=["TEST-1", "Updated Summary", "Updated Description"]):
            update_issue()

        mock_put.assert_called_once()

    @patch("requests.get")
    def test_list_issues(self, mock_get):
        """Test listing all issues in a project."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "issues": [
                {"key": "TEST-1", "fields": {"summary": "First issue", "status": {"name": "To Do"}}},
                {"key": "TEST-2", "fields": {"summary": "Second issue", "status": {"name": "In Progress"}}}
            ]
        }
        mock_get.return_value = mock_response

        with patch("builtins.input", side_effect=["TEST"]):
            list_issues()

        mock_get.assert_called_once()

    @patch("requests.delete")
    def test_delete_issue(self, mock_delete):
        """Test deleting an issue."""
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response

        with patch("builtins.input", side_effect=["TEST-1"]):
            delete_issue()

        mock_delete.assert_called_once()


if __name__ == "__main__":
    unittest.main()
