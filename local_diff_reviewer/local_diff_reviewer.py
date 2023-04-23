import os
import sys
from typing import Callable

import openai
import logging
from dotenv import load_dotenv
from html2text import html2text
from markdown import markdown
from unidiff import PatchSet

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalCodeReviewer:
    def __init__(self):
        logger.info("Initializing LocalCodeReviewer...")

    def message_reviewer(
        self,
        system_prompt: str,
        prompt: str,
        model="gpt-4",
        temperature=0.7,
        max_tokens=3000,
    ):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except openai.OpenAIError as e:
            print(f"Error calling OpenAI API: {e}")
            return ""

        return response.choices[0]['message']['content'].strip()

    def fetch_and_parse_diff(self, diff_path: str):
        try:
            with open(diff_path, 'r') as diff_file:
                raw_diff = diff_file.read()
        except IOError as e:
            logger.error(f"Error calling OpenAI API: {e}")
            sys.exit(1)
        patch = PatchSet(raw_diff)
        return patch

    def prepare_code_changes_messages(self, patch: PatchSet):
        code_changes = []
        for file in patch:
            if file.path != "package-lock.json":
                code_changes.append(f"```diff\n{file}\n```")
        return code_changes

    def review_code_changes(self, diff_path: str, commit_message: str, progress_callback: Callable = print):
        patch = self.fetch_and_parse_diff(diff_path)
        code_changes_messages = self.prepare_code_changes_messages(patch)

        code_changes_text = "\n".join(code_changes_messages)
        context_message = f"""The change has the following commit message: {commit_message}.
Here are the code changes in unidiff format:
{code_changes_text}

Your task is to:
- Review the code changes and provide feedback.
- If there are any bugs, highlight them.
- Provide details on missed use of best-practices.
- Does the code do what it says in the commit messages?
- Do not highlight minor issues and nitpicks.
- Use bullet points if you have multiple comments.
- Provide security recommendations if there are any."""

        system_prompt = """You are an AI language model designed to assist developers in reviewing code changes in a GitHub pull request. Analyze the provided code changes, title, and description carefully, and provide a comprehensive code review that includes:

- Identifying potential bugs or issues in the code.
- Pointing out any missed best-practices or areas for improvement.
- Assessing whether the code achieves its intended purpose based on the provided context.
- Focusing on significant concerns and avoiding minor nitpicks.
- Presenting your feedback in a clear, concise, and organized manner using bullet points for multiple comments.
- Suggesting security recommendations if applicable.

Remember, your goal is to help the developer improve their code by providing constructive feedback and guidance."""

        result = self.message_reviewer(
            system_prompt=system_prompt, prompt=context_message
        )
        result_html = markdown(result)
        result_text = html2text(result_html).strip()
        print("\nCode Review Results:\n", result_text)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python local_code_reviewer.py [diff_file_path] [commit_message]")
        sys.exit(1)

    diff_file_path = sys.argv[1]
    commit_message = sys.argv[2]

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        print("Please set the OPENAI_API_KEY environment variable.")
        sys.exit(1)

    openai.api_key = OPENAI_API_KEY

    code_review_assistant = LocalCodeReviewer()
    code_review_assistant.review_code_changes(diff_file_path, commit_message)
