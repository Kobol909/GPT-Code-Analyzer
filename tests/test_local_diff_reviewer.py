from local_diff_reviewer import LocalCodeReviewer

import pytest


class TestLocalCodeReviewer:

    # Tests that the code review assistant properly fetches and parses the diff file, prepares and formats the code changes messages correctly, and provides comprehensive feedback on the code changes.
    def test_review_code_changes(self):
        code_review_assistant = LocalCodeReviewer()
        diff_path = "tests/test_diff.diff"
        commit_message = "Test commit message"
        result = code_review_assistant.review_code_changes(diff_path, commit_message)
        assert "Code Review Results" in result

    # Tests that the LocalCodeReviewer class initializes properly.
    def test_init(self):
        code_review_assistant = LocalCodeReviewer()
        assert isinstance(code_review_assistant, LocalCodeReviewer)

    # Tests that providing an invalid diff file path results in an error and exit.
    def test_fetch_and_parse_diff_invalid_path(self):
        code_review_assistant = LocalCodeReviewer()
        diff_path = "invalid_path"
        with pytest.raises(SystemExit):
            code_review_assistant.fetch_and_parse_diff(diff_path)

    # Tests that providing an invalid commit message still initiates the code review process.
    def test_review_code_changes_invalid_commit_message(self):
        code_review_assistant = LocalCodeReviewer()
        diff_file_path = "test_diff.diff"
        commit_message = ""
        result = code_review_assistant.review_code_changes(diff_file_path, commit_message)
        assert "The change has the following commit message: ." in result

    # Tests that the message_reviewer() method properly calls the OpenAI API and returns a response.
    def test_message_reviewer(self):
        code_review_assistant = LocalCodeReviewer()
        system_prompt = "Test system prompt"
        prompt = "Test prompt"
        result = code_review_assistant.message_reviewer(system_prompt, prompt)
        assert result != ""

    # Tests that the prepare_code_changes_messages() method properly formats the code changes messages.
    def test_prepare_code_changes_messages(self):
        code_review_assistant = LocalCodeReviewer()
        diff_file_path = "test_diff.diff"
        patch = code_review_assistant.fetch_and_parse_diff(diff_file_path)
        result = code_review_assistant.prepare_code_changes_messages(patch)
        assert len(result) == 2
