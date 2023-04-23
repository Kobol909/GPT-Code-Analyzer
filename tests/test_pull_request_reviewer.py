from ossaudiodev import openmixer
from unidiff import PatchSet
from pull_request_reviewer import PRReviewer

import pytest
import openai



class TestPRReviewer:

    # Tests that PRReviewer initializes without errors.
    def test_PRReviewer_initialization(self):
        code_review_assistant = PRReviewer()
        assert code_review_assistant is not None

    # Tests that extract_pr_info returns the correct diff_url, description, and title.
    def test_extract_pr_info(self, monkeypatch):
        def mock_get_repo(repo_name):
            class MockPR:
                def __init__(self, diff_url, body, title):
                    self.diff_url = diff_url
                    self.body = body
                    self.title = title

            class MockRepo:
                def get_pull(self, pr_id):
                    return MockPR(
                        "https://github.com/test/repo/pull/1.diff",
                        "This is a test PR description.",
                        "Test PR Title",
                    )

            return MockRepo()

        monkeypatch.setattr("github.Github.get_repo", mock_get_repo)

        code_review_assistant = PRReviewer()
        diff_url, description, title = code_review_assistant.extract_pr_info(
            "https://github.com/test/repo/pull/1"
        )

        assert diff_url == "https://github.com/test/repo/pull/1.diff"
        assert description == "This is a test PR description."
        assert title == "Test PR Title"

    # Tests that review_pull_request handles an invalid PR URL gracefully.
    def test_review_pull_request_invalid_url(self, capsys):
        code_review_assistant = PRReviewer()
        code_review_assistant.review_pull_request("invalid_url")

        captured = capsys.readouterr()
        assert "Error calling OpenAI API" in captured.out

    # Tests that prepare_code_changes_messages returns a list of code change messages.
    def test_prepare_code_changes_messages(self):
        patch = PatchSet(
            """diff --git a/file1.txt b/file1.txt
            index 1234567..abcdefg 100644
            --- a/file1.txt
            +++ b/file1.txt
            @@ -1,2 +1,2 @@
            -Hello, world!
            +Hello, GitHub!
             How are you?
            diff --git a/file2.txt b/file2.txt
            index 1234567..abcdefg 100644
            --- a/file2.txt
            +++ b/file2.txt
            @@ -1,2 +1,2 @@
            -I am fine, thank you.
            +I am doing well, thanks for asking.
             How about you?
            """
        )
        expected_output = [
            "```diff\n"
            "diff --git a/file1.txt b/file1.txt\n"
            "index 1234567..abcdefg 100644\n"
            "--- a/file1.txt\n"
            "+++ b/file1.txt\n"
            "@@ -1,2 +1,2 @@\n"
            "-Hello, world!\n"
            "+Hello, GitHub!\n"
            " How are you?\n"
            "```",
            "```diff\n"
            "diff --git a/file2.txt b/file2.txt\n"
            "index 1234567..abcdefg 100644\n"
            "--- a/file2.txt\n"
            "+++ b/file2.txt\n"
            "@@ -1,2 +1,2 @@\n"
            "-I am fine, thank you.\n"
            "+I am doing well, thanks for asking.\n"
            " How about you?\n"
            "```",
        ]
        assert PRReviewer().prepare_code_changes_messages(patch) == expected_output

    # Tests that fetch_and_parse_diff handles an empty response gracefully.
    def test_fetch_and_parse_diff_empty_response(self, requests_mock):
        requests_mock.get("https://example.com", text="")
        assert PRReviewer().fetch_and_parse_diff("https://example.com") == PatchSet("")

    # Tests that message_prreviewer includes security recommendations in the code review message.
    def test_message_prreviewer_security_recommendations(self, monkeypatch):
        def mock_create(*args, **kwargs):
            return {
                "choices": [
                    {
                        "message": {
                            "content": "Here are some security recommendations:\n- Use HTTPS instead of HTTP.\n- Implement rate limiting to prevent brute-force attacks.\n"
                        }
                    }
                ]
            }

        monkeypatch.setattr(openai.ChatCompletion, "create", mock_create)

        result = PRReviewer().message_prreviewer(
            system_prompt="",
            prompt="",
        )
        assert "Here are some security recommendations:" in result