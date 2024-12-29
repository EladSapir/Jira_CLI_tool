# Jira CLI Tool

## Overview
This command-line application integrates with Jira to manage project issues efficiently. It supports connecting to your Jira account, retrieving, creating, updating, and deleting issues, and listing all issues in a project.

## Features
1. **Setup**: Configure your Jira base URL, email, and API token securely.
2. **Get an Issue**: Fetch and display details of a specific issue.
3. **Create an Issue**: Add a new issue by specifying project key, summary, and type.
4. **Update an Issue**: Modify the summary or description of an existing issue.
5. **List Issues**: Display all issues in a specified project.
6. **Delete an Issue**: Remove an issue by its key.

## Enhancements
- **Base64 Encoding**: Credentials are securely stored in an encoded format to protect sensitive data.
- **Improved CLI Design**: A user-friendly, color-coded interface for easy navigation.
- **Input Validation**: Ensures user inputs are valid and meaningful.
- **Additional Jira Features**: supports updating issue, listing all issues in project and deleting issue.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/EladSapir/Jira_CLI_tool
   cd Jira_CLI_tool
   ```
2. Set up a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```


## Usage
Run the application:
```bash
python jira_cli_tool.py
```
Follow the menu options to perform operations such as retrieving, creating, updating, listing, and deleting Jira issues.

## Testing
Run unit tests:
```bash
python -m unittest test_main_script.py
```

## Notes
- Credentials are Base64-encoded for basic security.
- Ensure your Jira account has the necessary permissions to perform the actions.

## Future Improvements
- Stronger encryption for credentials.
- Additional functionalities like assigning issues or adding comments.

