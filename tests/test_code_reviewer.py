from ossaudiodev import openmixer
from code_reviewer import CodeReviewer

import pytest
import openai


class TestCodeReviewer:
    @pytest.fixture(scope="function")
    # Returns a CodeReviewer instance.
    def CodeReviewer(self):
        return CodeReviewer()

    # Tests that the message_reviewer method returns the expected response.
    def test_message_reviewer(self, code_reviewer, mocker):
        mocker.patch.object(openai.ChatCompletion, "create", return_value={"choices": [{"message": {"content": "Great job!"}}]})
        result = code_reviewer.message_reviewer("test system prompt", "test prompt")
        assert result == "Great job!"

    # Tests that CodeReviewer is initialized successfully.
    def test_init_success(self):
        code_review_assistant = CodeReviewer()
        assert code_review_assistant is not None

    # Tests that an IOError is raised when an invalid code file path is provided.
    def test_invalid_file_path(self, monkeypatch):
        def mock_open(*args, **kwargs):
            raise IOError("File not found")

        monkeypatch.setattr("builtins.open", mock_open)
        code_review_assistant = CodeReviewer()
        with pytest.raises(IOError):
            code_review_assistant.fetch_and_parse_code("invalid_file_path.py")

    # Tests that a sys.exit(1) is called when commit message is missing.
    def test_missing_commit_message(self, capsys):
        with pytest.raises(SystemExit):
            CodeReviewer()
            captured = capsys.readouterr()
            assert "Usage: python code_reviewer.py [code_file_path] [commit_message]" in captured.out

    # Tests that a sys.exit(1) is called when the OPENAI_API_KEY environment variable is missing.
    def test_openai_api_key_missing(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(SystemExit):
            CodeReviewer()

    # Tests that an error is raised when the code file is too large for OpenAI API.
    def test_large_code_file(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test_key")
        code_review_assistant = CodeReviewer()
        with pytest.raises(Exception):
            code_review_assistant.review_code_changes("large_code_file.py", "test commit message")

    # Tests that the code review assistant provides constructive feedback using OpenAI API.
    def test_review_code_changes(self, monkeypatch, mocker):
        monkeypatch.setenv("OPENAI_API_KEY", "test_key")
        code_review_assistant = CodeReviewer()
        mocker.patch.object(openai.ChatCompletion, "create", return_value={"choices": [{"message": {"content": "Great job!"}}]})
        result = code_review_assistant.review_code_changes("test_code_file.py", "test commit message")
        assert "Great job!" in result
