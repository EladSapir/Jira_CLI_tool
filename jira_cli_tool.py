import argparse
import configparser
import base64
import requests
import sys

# ANSI Color Codes
RESET = "\033[0m"
BOLD = "\033[1m"
BLUE = "\033[1;34m"
GREEN = "\033[1;32m"
CYAN = "\033[1;36m"
RED = "\033[1;31m"

# Constants
CONFIG_FILE = "config.ini"


# Color Utility Function
def colored(text, color):
    """Wrap text with the given ANSI color."""
    return f"{color}{text}{RESET}"


# Base64 Encode/Decode Functions
def encode_base64(text):
    """Encode text using Base64."""
    return base64.b64encode(text.encode()).decode()


def decode_base64(encoded_text):
    """Decode Base64 text."""
    return base64.b64decode(encoded_text.encode()).decode()


# Config Management
def save_config(base_url, email, api_token):
    """Save configuration to a file with Base64 encoding."""
    encoded_email = encode_base64(email)
    encoded_api_token = encode_base64(api_token)

    config = configparser.ConfigParser()
    config['JIRA'] = {
        'base_url': base_url,
        'email': encoded_email,
        'api_token': encoded_api_token
    }
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)


def load_config():
    """Load and decode configuration from a file."""
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if 'JIRA' not in config:
        print(colored("Error: Configuration not found. Please run setup.", RED))
        sys.exit(1)

    base_url = config['JIRA']['base_url']
    email = decode_base64(config['JIRA']['email'])
    api_token = decode_base64(config['JIRA']['api_token'])
    return {"base_url": base_url, "email": email, "api_token": api_token}


# Helper Function for Headers
def get_headers(email, api_token):
    """Generate HTTP headers for authentication."""
    credentials = f"{email}:{api_token}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json"
    }


# Core Functionalities
def setup():
    """Set up Jira CLI configuration."""
    base_url = input("Enter your Jira base URL (e.g., https://yourdomain.atlassian.net): ").strip()
    email = input("Enter your Jira email: ").strip()
    api_token = input("Enter your Jira API token: ").strip()
    save_config(base_url, email, api_token)
    print(colored("Configuration saved successfully!", GREEN))


def get_issue():
    """Fetch a Jira issue by key."""
    config = load_config()
    headers = get_headers(config['email'], config['api_token'])
    issue_key = input("Enter the Jira issue key (e.g., PROJ-123): ").strip()

    url = f"{config['base_url']}/rest/api/3/issue/{issue_key}"
    print(colored(f"Fetching issue from URL: {url}", BLUE))
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        issue = response.json()
        print("\n" + colored("Issue Details:", GREEN))
        print(f"Key: {issue['key']}")
        print(f"Summary: {issue['fields']['summary']}")
        print(f"Status: {issue['fields']['status']['name']}")
    else:
        print(colored(f"Error: Unable to fetch issue. {response.status_code} - {response.text}", RED))


def create_issue():
    """Create a new Jira issue."""
    config = load_config()
    headers = get_headers(config['email'], config['api_token'])

    project_key = input("Enter the project key: ").strip()
    summary = input("Enter the issue summary: ").strip()
    issue_type = input("Enter the issue type (e.g., Bug, Task): ").strip()

    url = f"{config['base_url']}/rest/api/3/issue"
    payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": issue_type}
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        issue = response.json()
        print(colored(f"Issue created successfully! Key: {issue['key']}", GREEN))
    else:
        print(colored(f"Error: Unable to create issue. {response.status_code} - {response.text}", RED))


def update_issue():
    """Update an existing Jira issue."""
    config = load_config()
    headers = get_headers(config['email'], config['api_token'])
    issue_key = input("Enter the Jira issue key to update (e.g., PROJ-123): ").strip()

    new_summary = input("Enter the new summary (leave blank to keep current): ").strip()
    new_description = input("Enter the new description (leave blank to keep current): ").strip()

    if not new_summary and not new_description:
        print(colored("Error: At least one field (summary or description) must be updated.", RED))
        return

    url = f"{config['base_url']}/rest/api/3/issue/{issue_key}"
    payload = {"fields": {}}

    if new_summary:
        payload["fields"]["summary"] = new_summary
    if new_description:
        payload["fields"]["description"] = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": new_description
                        }
                    ]
                }
            ]
        }

    response = requests.put(url, json=payload, headers=headers)

    if response.status_code == 204:
        print(colored("Issue updated successfully!", GREEN))
    else:
        print(colored(f"Error: Unable to update issue. {response.status_code} - {response.text}", RED))


def list_issues():
    """List all issues in a Jira project."""
    config = load_config()
    headers = get_headers(config['email'], config['api_token'])
    project_key = input("Enter the Jira project key: ").strip()

    url = f"{config['base_url']}/rest/api/3/search?jql=project={project_key}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        issues = response.json()["issues"]
        print("\n" + colored("List of Issues:", GREEN))
        for issue in issues:
            print(f"- {issue['key']}: {issue['fields']['summary']} (Status: {issue['fields']['status']['name']})")
    else:
        print(colored(f"Error: Unable to list issues. {response.status_code} - {response.text}", RED))


def delete_issue():
    """Delete a Jira issue by key."""
    config = load_config()
    headers = get_headers(config['email'], config['api_token'])
    issue_key = input("Enter the Jira issue key to delete (e.g., PROJ-123): ").strip()

    url = f"{config['base_url']}/rest/api/3/issue/{issue_key}"
    response = requests.delete(url, headers=headers)

    if response.status_code == 204:
        print(colored("Issue deleted successfully!", GREEN))
    else:
        print(colored(f"Error: Unable to delete issue. {response.status_code} - {response.text}", RED))


# Menu Display
def display_menu():
    """Display the main menu."""
    print("\n" + "=" * 60)
    print(colored("Welcome to the Jira CLI Tool", CYAN))
    print("=" * 60)
    print(colored("1. Get an Issue", BLUE))
    print(colored("2. Create an Issue", BLUE))
    print(colored("3. Update an Issue", BLUE))
    print(colored("4. List All Issues in a Project", BLUE))
    print(colored("5. Delete an Issue", BLUE))
    print(colored("6. Setup Configuration", CYAN))
    print(colored("7. Exit", RED))
    print("=" * 60)


# Main Loop
def main():
    """Main function to display menu and handle user choices."""
    parser = argparse.ArgumentParser(description="Jira CLI Tool")
    parser.add_argument("--setup", action="store_true", help="Configure the application to connect to Jira")
    args = parser.parse_args()

    if args.setup:
        setup()
        return

    while True:
        display_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            get_issue()
        elif choice == "2":
            create_issue()
        elif choice == "3":
            update_issue()
        elif choice == "4":
            list_issues()
        elif choice == "5":
            delete_issue()
        elif choice == "6":
            setup()
        elif choice == "7":
            print(colored("Goodbye!", GREEN))
            break
        else:
            print(colored("Invalid choice. Please try again.", RED))


if __name__ == "__main__":
    main()
