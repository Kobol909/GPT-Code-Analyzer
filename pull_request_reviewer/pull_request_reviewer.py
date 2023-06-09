import os
import sys
from typing import Callable

import openai
import requests
import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from html2text import html2text
from markdown import markdown
from unidiff import PatchSet
from github import Github

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PRReviewer:
    def __init__(self):
        print("Initializing CodeReviewAssistant...")

    def message_prreviewer(
        self,
        system_prompt: str,
        prompt: str,
        model="gpt-4",
        temperature=0.7,
        max_tokens=3000,
    ) -> str:
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
        except openai.Error as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return ""

        return response.choices[0]['message']['content'].strip()

    def extract_pr_info(self, pr_url: str):
        pr_id = int(pr_url.split('/')[-1])
        repo_name = f"{pr_url.split('/')[-3]}/{pr_url.split('/')[-2]}"
        gh = Github(os.getenv("GITHUB_TOKEN"))
        repo = gh.get_repo(repo_name)
        pr = repo.get_pull(pr_id)

        diff_url = pr.diff_url
        description = pr.body
        title = pr.title

        return diff_url, description, title

    def fetch_and_parse_diff(self, diff_url: str):
        with requests.get(diff_url) as response:
            raw_diff = response.text
        patch = PatchSet(raw_diff)
        return patch

    def prepare_code_changes_messages(self, patch: PatchSet):
        code_changes = []
        for file in patch:
            if file.path != "package-lock.json":
                code_changes.append(f"```diff\n{file}\n```")
        return code_changes

    def review_pull_request(self, pr_url: str, progress_callback: Callable = print):
        diff_url, description, title = self.extract_pr_info(pr_url)

        patch = self.fetch_and_parse_diff(diff_url)
        code_changes_messages = self.prepare_code_changes_messages(patch)

        code_changes_text = "\n".join(code_changes_messages)
        context_message = f"""The change has the following title: {title}.
{description}
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

        result = self.message_prreviewer(
            system_prompt=system_prompt, prompt=context_message
        )
        result_html = markdown(result)
        result_text = html2text(result_html).strip()
        print("\nCode Review Results:\n", result_text)


if __name__ == "__main__":
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    openai.api_key = OPENAI_API_KEY

    pr_url = sys.argv[1]  # Replace with the GitHub Pull Request URL you want to review

    code_review_assistant = PRReviewer()
    code_review_assistant.review_pull_request(pr_url)
