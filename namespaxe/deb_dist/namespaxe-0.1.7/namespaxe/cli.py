from datetime import datetime
import os
import json
import base64
import requests
import click
from tabulate import tabulate
import yaml

CONFIG_DIR = os.path.expanduser("~/.namespaxe")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


class NamespaxeCLI:
    def __init__(self):
        self.config_dir = CONFIG_DIR
        self.config_file = CONFIG_FILE
        self.base_protocol = "https"
        self.login_url = "auth0.pyincorporation.com/tool-authenticate"
        self.upstream_url = "pycloud.pyincorporation.com"

    def check_config_exists(self):
        if not os.path.exists(self.config_file):
            click.echo("No config file found. Please login using 'namespaxe login'.")
            return False
        return True

    def load_token(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                try:
                    auth = json.load(f).get("auths", {}).get(f"{self.base_protocol}://{self.login_url}", {}).get("auth")
                    if auth:
                        decoded_credentials = base64.b64decode(auth).decode().split(":")
                        return {"username": decoded_credentials[0], "password": decoded_credentials[1]}
                except Exception:
                    return False
        return None

    def save_token(self, username, password):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        data_to_save = {
            "auths": {
                f"{self.base_protocol}://{self.login_url}": {
                    "auth": encoded_credentials
                }
            }
        }

        with open(self.config_file, 'w') as f:
            json.dump(data_to_save, f, indent=4)

    def get_token(self):
        try:
            base_url = f"{self.base_protocol}://auth0.pyincorporation.com/data"
            headers = {"Accept": "application/json"}

            response = requests.get(base_url, headers=headers)

            if response.status_code == 200:
                csrf_token = response.cookies.get('csrftoken')
                session_id = response.cookies.get('sessionid')
                return {
                    'csrf_token': csrf_token,
                    'session_id': session_id,
                    **response.json()
                }
            else:
                click.echo(f"Request failed with status code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            click.echo(f"An error occurred: {e}")
            return None

    def login_to_server(self, username=None, password=None):
        if username and password:
            click.echo(f"Logging in with provided credentials for {username}...")
        else:
            credentials = self.load_token()
            if credentials:
                click.echo("Authenticating with existing credentials...")
                username = credentials.get('username')
                password = credentials.get('password')
            else:
                username = click.prompt('Username')
                password = click.prompt('Password', hide_input=True)
        
        token_data = self.get_token()
        if not token_data:
            click.echo("Failed to fetch the authentication token.")
            return

        csrf_token = token_data.get('csrf_token')
        session_id = token_data.get('session_id')

        credentials = {
            'username': username,
            'password': password
        }

        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            base_url = f"{self.base_protocol}://{self.login_url}"
            response = requests.post(
                base_url,
                data=json.dumps(credentials),
                headers=headers,
                cookies={'csrftoken': csrf_token, 'sessionid': session_id},
            )

            if response.status_code == 200:
                response_data = response.json()
                if response_data['status']:
                    click.echo(f'WARNING! Your password will be stored unencrypted in {self.config_file}')
                    click.echo()
                    click.echo("Login successful!")
                    self.save_token(username, password)
                    return response_data
                else:
                    click.echo(f"Login failed: {response_data.get('message')}")
            else:
                click.echo(f"Login failed! Status code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            click.echo(f"An error occurred: {e}")

    def handle_http_error(self, status_code):
        if status_code == 400:
            return "Bad Request: The server could not understand the request due to invalid syntax."
        elif status_code == 401:
            return "Unauthorized: You are not authorized to access this resource. Please check your credentials."
        elif status_code == 403:
            return "Forbidden: You do not have the necessary permissions to access this resource."
        elif status_code == 404:
            return "Not Found: The requested resource could not be found."
        elif status_code == 500:
            return "Internal Server Error: The server encountered an error and could not complete the request."
        elif status_code == 502:
            return "Bad Gateway: The server received an invalid response from an upstream server."
        elif status_code == 503:
            return "Service Unavailable: The server is currently unable to handle the request."
        elif status_code == 504:
            return "Gateway Timeout: The server took too long to respond."
        else:
            return f"Unexpected error: Received status code {status_code}."

    def list_resources(self, resource_type, wide=False, clean=False):
        if not self.check_config_exists():
            return

        credentials = self.load_token()
        if not credentials:
            click.echo("Failed to load credentials. Please log in again.")
            return

        token_data = self.get_token()
        if not token_data:
            click.echo("Failed to fetch the authentication token.")
            return

        csrf_token = token_data.get('csrf_token')
        session_id = token_data.get('session_id')

        request_data = {
            'username': credentials['username'],
            'password': credentials['password'],
            'resource_type': resource_type
        }

        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            url = f"{self.base_protocol}://{self.upstream_url}/list/{resource_type}"
            
            response = requests.post(
                url,
                data=json.dumps(request_data),
                headers=headers,
                cookies={'csrftoken': csrf_token, 'sessionid': session_id},
            )

            if response.status_code == 200:
                data = response.json()
                
                if clean:
                    click.echo(json.dumps(data, indent=4))
                elif data.get('body') and data['body'].get('data'):
                    table_data = []

                    for namespace in data['body']['data']:
                        ns_name = namespace.get('name')
                        cluster_name = namespace.get('cluster', {}).get('name')
                        package = namespace.get('package_name')
                        created_at = namespace.get('created_at')

                        if wide:
                            table_data.append([ns_name, cluster_name, package, created_at])
                        else:
                            table_data.append([ns_name])

                    headers = ["Namespace Name", "Cluster", "Package", "Created At"] if wide else ["Namespace Name"]
                    
                    click.echo(tabulate(table_data, headers=headers, tablefmt="pretty"))
                else:
                    click.echo("No namespaces found.")
            else:
                error_message = self.handle_http_error(response.status_code)
                click.echo(error_message)

        except requests.exceptions.RequestException as e:
            click.echo(f"An error occurred: {e}")

    def date_convert(self, date_string):
        date_object = datetime.strptime(date_string, "%Y-%m-%d")
        formatted_date = date_object.strftime("%b, %d %Y")
        return formatted_date
    
    def install_k8s_config(self, resource_type, namespace_name):
        if not self.check_config_exists():
            return

        credentials = self.load_token()
        if not credentials:
            click.echo("Failed to load credentials. Please log in again.")
            return

        token_data = self.get_token()
        if not token_data:
            click.echo("Failed to fetch the authentication token.")
            return

        csrf_token = token_data.get('csrf_token')
        session_id = token_data.get('session_id')

        request_data = {
            'username': credentials['username'],
            'password': credentials['password'],
            'resource_name': namespace_name,
            'resource_type': resource_type
        }

        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            url = f"{self.base_protocol}://{self.upstream_url}/config/{resource_type}/{namespace_name}"

            response = requests.post(
                url,
                data=json.dumps(request_data),
                headers=headers,
                cookies={'csrftoken': csrf_token, 'sessionid': session_id},
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('status'):
                    config_content = data.get('data', {})

                    config_yaml = yaml.dump(config_content, default_flow_style=False)
                    kubeconfig_dir = os.path.expanduser("~/.kube")
                    kubeconfig_file = os.path.join(kubeconfig_dir, "config")

                    if not os.path.exists(kubeconfig_dir):
                        os.makedirs(kubeconfig_dir)

                    with open(kubeconfig_file, 'w') as f:
                        f.write(config_yaml)

                    click.echo(f"Kubernetes configuration for namespace '{namespace_name}' has been installed at {kubeconfig_file}")
                else:
                    if data.get('message'):
                        click.echo(data.get('message'))
                    else:
                        click.echo("Failed to fetch Kubernetes configuration.")
            else:
                error_message = self.handle_http_error(response.status_code)
                click.echo(error_message)

        except requests.exceptions.RequestException as e:
            click.echo(f"An error occurred: {e}")
        except Exception as e:
            click.echo(f"An error occurred: {e}")
            
    def describe_resource(self, resource_type, resource_name, wide=False, clean=False):
        if not self.check_config_exists():
            return

        credentials = self.load_token()
        if not credentials:
            click.echo("Failed to load credentials. Please log in again.")
            return

        token_data = self.get_token()
        if not token_data:
            click.echo("Failed to fetch the authentication token.")
            return

        csrf_token = token_data.get('csrf_token')
        session_id = token_data.get('session_id')

        request_data = {
            'username': credentials['username'],
            'password': credentials['password'],
            'resource_type': resource_type,
            'resource_name': resource_name
        }

        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            url = f"{self.base_protocol}://{self.upstream_url}/describe/{resource_type}/{resource_name}"

            response = requests.post(
                url,
                data=json.dumps(request_data),
                headers=headers,
                cookies={'csrftoken': csrf_token, 'sessionid': session_id},
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('body') and data['body'].get('data'):
                    description_data = data['body']['data'].get('name', {})
                    package_data = data['body']['data'].get('package', {})
                    package_features = package_data.get('package_features', {})

                    important_fields = {
                        "Namespace Name": description_data.get('name', 'N/A'),
                        "Cluster Name": description_data.get('cluster', {}).get('name', 'N/A'),
                        "Cluster API URL": description_data.get('cluster', {}).get('api_url', 'N/A'),
                        "Cluster Scrape URL": description_data.get('cluster', {}).get('scrape_url', 'N/A'),
                        "Cluster Region": description_data.get('cluster', {}).get('region', {}).get('region', 'N/A'),
                    }

                    if clean:
                        click.echo(json.dumps(description_data, indent=4))
                    else:
                        table_data = [[key, value] for key, value in important_fields.items()]

                        if wide:
                            cpu_val = package_features.get('cpu')
                            ram_val = package_features.get('ram')
                            volume_unit = package_features.get('volume_size_unit', '')

                            extra_fields = {
                                "CPU": f"{int(cpu_val * 1000)}m" if isinstance(cpu_val, (int, float)) else 'N/A',
                                "RAM": f"{ram_val}Mi" if ram_val else 'N/A',
                                "Pods": package_features.get('pods', 'N/A'),
                                "Secrets": package_features.get('secrets', 'N/A'),
                                "ConfigMaps": package_features.get('configmaps', 'N/A'),
                                "Services": package_features.get('service', 'N/A'),
                                "Ingress": package_features.get('ingress', 'N/A'),
                                "PVC Count": package_features.get('pvc_count', 'N/A'),
                                "Total Storage Requests": f"{package_features.get('total_storage_requests', 'N/A')}{volume_unit}i",
                                "Max PVC Storage Request": f"{package_features.get('max_pvc_storage_request', 'N/A')}{volume_unit}i",
                            }

                            for key, value in extra_fields.items():
                                table_data.append([key, value])

                        click.echo(tabulate(table_data, headers=["Field", "Value"], tablefmt="pretty"))
                else:
                    if data.get('message'):
                        click.echo(data.get('message'))
                    else:
                        click.echo("No details found for the specified resource.")
            else:
                error_message = self.handle_http_error(response.status_code)
                click.echo(error_message)



        except requests.exceptions.RequestException as e:
            click.echo(f"An error occurred: {e}")


    def show_help(self):
        help_text = """
        namespaxe CLI Tool

        Commands:
            login               - Log in to the web server. 
                                Usage: namespaxe login --username <username> --password <password>
                                
            list <resource>     - List resources. 
                                Usage: namespaxe list <resource> [--wide] [--clean]
                                Example: namespaxe list ns  --wide
                                
            describe <res> <name> - Describe a specific resource.
                                Usage: namespaxe describe <resource> <resource_name> [--wide] [--clean]
                                Example: namespaxe describe ns <namespace-name> --wide

            config  - Install Kubernetes config for a specific resource.
                                Usage: namespaxe config <resource> <resource_name>
                                Example: namespaxe config ns <namespace-name>

            help                - Show this help menu.

        Options:
            --wide              - Show extra details when listing or describing resources.
            --username          - Specify the username for logging into the server.
            --password          - Specify the password for logging into the server.
            --clean             - Print raw API response without formatting.
        """
        click.echo(help_text)


@click.command()
@click.argument('command')
@click.argument('resource', required=False)
@click.argument('resource_name', required=False)
@click.option('--wide', is_flag=True, help='Show extra details')
@click.option('--username', help='Username for login')
@click.option('--password', help='Password for login')
@click.option('--clean', is_flag=True, help='Print raw API response without formatting')
def main(command, resource, resource_name, wide, username, password, clean):
    """Main entry point for the CLI tool."""
    cli = NamespaxeCLI()

    if command == "login":
        cli.login_to_server(username, password)
    elif command == "list":
        if not resource:
            click.echo(f"Usage of {command} command: namespaxe list <argument>")
            return
        cli.list_resources(resource, wide, clean)
    elif command == "describe":
        if not resource or not resource_name:
            click.echo(f"Usage of {command} command: namespaxe describe <argument> <argument>")
            return
        cli.describe_resource(resource, resource_name, wide, clean)
    elif command == "config":
        if not resource or not resource_name:
            click.echo(f"Usage of {command} command: namespaxe config <resource> <resource-name>")
            return
        cli.install_k8s_config(resource, resource_name)
    elif command == "help":
        cli.show_help()
    else:
        click.echo(f"Unknown command: {command}. Use 'namespaxe help' for a list of commands.")

if __name__ == "__main__":
    main()

