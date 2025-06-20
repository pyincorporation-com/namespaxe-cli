# Namespaxe CLI Tool

## Overview

A command-line interface for managing namespaces in Namespaxe's infrastructure.

## Features

- 🔐 Secure authentication with token management
- 📜 List and inspect namespace resources
- ⚡ Install Kubernetes configurations
- ✨ Multiple output formats (table, wide, JSON)

## Installation

```bash
pip install namespaxe
```

## Usage

To use the `namespaxe` CLI tool, run the command followed by the desired operation:

### Commands

- **Login:**

  - `namespaxe login`
  - `namespaxe login --username 'my-username' --password 'mypassword'`

    **Behavior:**

    - Prompts for credentials if not provided

    - Stores credentials in ~/.namespaxe/config.json (base64 encoded)

    - Uses CSRF tokens and session cookies for security

    **Implementation Details:**

    - Makes POST request to upstream authentication server

    - Credentials are validated against Auth0 service

    - Successful login creates/updates config file with 600 permissions

- **List Resources:**

  - `namespaxe list <resource>`
  - `namespaxe list <resource> --wide`
  - `namespaxe list <resource> --clean`

    **Supported Resources:**

        ns (namespaces)

    Options: Flag Description

    - --wide Shows cluster, subscription package and timestamps
    - --clean Outputs raw JSON response

    Implementation Details:

    - Makes POST request to upstream server

    - Returns array of objects:

      - Namespace name (always shown)

      - Cluster name (wide mode)

      - subscription package name (wide mode)

      - Creation timestamp (wide mode)

- **Describe Resource:**

  - `namespaxe describe <resource> <resource_name>`
  - `namespaxe describe <resource> <resource_name> --wide`
  - `namespaxe describe <resource> <resource_name> --clean`

    **Supported Resources:**

        ns (namespaces)

    Options: Flag Description

    - --wide Shows cluster, resource limits, and timestamps
    - --clean Outputs raw JSON response

    Implementation Details:

    - Makes POST request to upstream server

    - Returns an object of:

      - Namespace name (always shown)

      - Cluster details (always shown)

      - Resource limits (wide mode)

      - Creation timestamp (wide mode)

- **Install Kubernetes Configuration:** `namespaxe config <resource> <namespace_name>`

  **Details:**

  - Saves configuration to ~/.kube/config

  - Overwrites existing configuration

  - Requires valid namespace permissions

  - Creates ~/.kube directory if missing

  **Implementation Details:**

  - POSTs to https://pycloud.pyincorporation.com/config/{resource}/{name}

  - Validates response before writing

  - Config is converted from JSON to YAML format

  - Sets 600 permissions on created files

- **Help:** `namespaxe help`

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

**Prerequisites**

- Python 3.6+

- Required packages: click, requests, pyyaml, tabulate
