# Cloudflare DDNS Client

[![Script Still Working](https://github.com/ikhwanperwira/cloudflare-ddns-client/actions/workflows/main.yml/badge.svg)](https://github.com/ikhwanperwira/cloudflare-ddns-client/actions/workflows/main.yml)

## Introduction
The `cf_ddns.py` script is a command-line tool that allows you to update your Cloudflare DNS records with your current public IP address. This is useful for dynamic (ephemeral) public IP addresses where you want to keep your DNS records up to date.

## Prerequisites
Before using `cf_ddns.py`, make sure you have the following prerequisites installed:

- Python 3.x (No need `pip`, all dependencies using built-in)
- Cloudflare API Token with these permissions:
  ```
  All zones - Zone Settings:Read, Zone:Read, DNS:Edit
  ```

## Installation
Clone the repository:
  ```shell
  git clone https://github.com/ikhwanperwira/cloudflare-ddns-client.git
  ```

  OR

  ```shell
  wget https://raw.githubusercontent.com/ikhwanperwira/cloudflare-ddns-client/main/cf_ddns.py && chmod +x cf_ddns.py && mv cf_ddns.py /usr/bin
  ```

## Usage
To use `cf_ddns.py`, follow these steps:

1. Open a terminal or command prompt.

2. Navigate to the project directory:
    ```shell
    cd ./cloudflare-ddns-client
    ```

3. Run the script with the following command:
    ```shell
    python3 cf_ddns.py python cf_ddns.py <API_TOKEN> <DOMAIN> <RECORD_NAME> <TTL> <PROXIED> <SOURCE_IP (OPTIONAL)>
    ```

    Example:
    ```shell
    python3 cf_ddns.py <API_TOKEN> example.com subdomain 3600 true 172.16.0.2
    ```

4. The script will retrieve your current public IP address and update the specified DNS record with the new IP address.

## Startup Configuration

To configure the `cf_ddns.py` script to run as a systemd service on Linux, follow these steps:

1. Move `cf_ddns.py` to `/usr/bin`:
  ```shell
  sudo mv cf_ddns.py /usr/bin
  ```

2. Create a new service file using a text editor. For example, create a file called `cf_ddns.service` in the `/etc/systemd/system/` directory.
    ```shell
    sudo vi /etc/systemd/system/cf_ddns.service
    ```

3. Add the following content to the `cf_ddns.service` file:
    ```
    [Unit]
    Description=Cloudflare DDNS Client
    After=network.target

    [Service]
    Type=simple
    ExecStart=/usr/bin/cf_ddns.py <API_TOKEN> <DOMAIN> <RECORD_NAME> <TTL> <PROXIED> <SOURCE_IP (OPTIONAL)>

    [Install]
    WantedBy=multi-user.target
    ```

4. Enable the service to start on boot and start the service:
    ```shell
    sudo systemctl enable cf_ddns.service
    sudo systemctl start cf_ddns.service
    ```

## License
This project is licensed under the [MIT License](LICENSE).
