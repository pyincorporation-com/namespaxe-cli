import requests
import sys

def login_to_server(base_url, username, password):
    login_url = f"{base_url}/login"  # Replace with your actual login endpoint
    credentials = {
        'username': username,
        'password': password
    }

    try:
        response = requests.post(login_url, data=credentials)

        if response.status_code == 200:
            print("Login successful!")
            # Additional functionality can be added here
        else:
            print("Login failed! Please check your credentials.")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def show_help():
    help_text = """
    namespaxe CLI Tool

    Commands:
        login     - Log in to the web server
        help      - Show this help menu
    """
    print(help_text)

def main():
    if len(sys.argv) < 2:
        print("No command provided. Use 'namespaxe help' for a list of commands.")
        return

    command = sys.argv[1]

    if command == "login":
        base_url = input("Enter the base URL of the web server (e.g., http://example.com): ")
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        login_to_server(base_url, username, password)
    elif command == "help":
        show_help()
    else:
        print(f"Unknown command: {command}. Use 'namespaxe help' for a list of commands.")

if __name__ == "__main__":
    main()
