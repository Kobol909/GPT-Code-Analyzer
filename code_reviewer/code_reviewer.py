import os
import sys
from typing import Callable

import openai
import logging
from dotenv import load_dotenv
from html2text import html2text
from markdown import markdown

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeReviewer:
    def __init__(self):
        logging.info("Initializing CodeReviewer...")

    def message_reviewer(
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
            logging.error(f"Error calling OpenAI API: {e}")
            raise

        return response.choices[0]['message']['content'].strip()

    def fetch_and_parse_code(self, code_file_path: str):
        try:
            with open(code_file_path, 'r') as code_file:
                code = code_file.read()
        except (IOError, OSError) as e:
            logging.error(f"Error reading file: {e}")
            raise
        return code

    def review_code_changes(self, code_file_path: str, commit_message: str, progress_callback: Callable[[str], None] = print):
        code = self.fetch_and_parse_code(code_file_path)
        context_message = f"""The change has the following commit message: {commit_message}.
Here is the code:
```python
{code}
```

Your task is to:
- Review the code and provide feedback.
- If there are any bugs, highlight them.
- Provide details on missed use of best-practices.
- Does the code do what it says in the commit messages?
- Do not highlight minor issues and nitpicks.
- Use bullet points if you have multiple comments.
- Provide security recommendations if there are any."""

        system_prompt = """You are an AI language model designed to assist developers in reviewing code. Analyze the provided code and commit message carefully, and provide a comprehensive code review that includes:

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
        print("Usage: python code_reviewer.py [code_file_path] [commit_message]")
        sys.exit(1)

    code_file_path = sys.argv[1]
    commit_message = sys.argv[2]

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        print("Please set the OPENAI_API_KEY environment variable.")
        sys.exit(1)

    openai.api_key = OPENAI_API_KEY

    code_review_assistant = CodeReviewer()
    code_review_assistant.review_code_changes(code_file_path, commit_message)

