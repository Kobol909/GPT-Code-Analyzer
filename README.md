# GPT-Code-Analyzer

GPT-Code-Analyzer is a collection of Python scripts that utilize the OpenAI GPT-4 model to review and analyze code changes in different contexts, such as single code files, local diff files, and GitHub pull requests.

## Scripts

### code-reviewer

The `code-reviewer` script analyzes a single code file and provides feedback based on the commit message.

**Usage:**

```bash
python code-reviewer/code-reviewer.py [code_file_path] [commit_message]
```

### **local-reviewer**

The **`local-reviewer`** script analyzes code changes in a local diff file and provides feedback based on the commit message.

**Usage:**

```bash
python local-reviewer/local-reviewer.py [diff_file_path] [commit_message]
```

### **pull-request-reviewer**

The **`pull-request-reviewer`** script reviews code changes in a GitHub pull request and provides feedback.

**Usage:**

```bash
python pull-request-reviewer/pull-request-reviewer.py [pull_request_url]
```

## **Prerequisites**

- Python 3.6 or higher
- An OpenAI API key
- A GitHub API token (optional, only required for **`pull-request-reviewer.py`**)

## **Installation**

- Clone the repository:

```bash
git clone https://github.com/your_username/GPT-Code-Analyzer.git
```

- Install the required Python packages:

```bash
pip install -r requirements.txt
```

- Set up the **`.env`** files:

Copy the **`.env.template`** file to each script's folder and rename it to **`.env`**. Replace the placeholder values with your actual OpenAI API key and, if needed, your GitHub API token.

## **Future Improvements**

While the current project is functional and ready for use, we have identified some areas for future improvements:

1. [] **Add unit tests and continuous integration**: Implement unit tests for the scripts to ensure code quality and prevent regressions. Set up continuous integration to automatically run the tests on each commit.
2. [] **Improve error handling and edge-case coverage**: Enhance the scripts by adding more error handling and covering edge cases to make the code more robust.
3. [] **Support for other version control platforms**: Extend the project to support code review and analysis for other version control platforms, such as GitLab and Bitbucket.
4. [] **Support for other programming languages**: Adapt the code review process to handle other programming languages in addition to Python.
5. [] **Keep up with GPT model improvements**: Continuously monitor the progress and improvements in the GPT models and update the project accordingly to take advantage of new features and performance enhancements.

## **Contributing**

Contributions are welcome! Feel free to submit issues and pull requests for new features or improvements.

## **License**

**[MIT](https://choosealicense.com/licenses/mit/)**
