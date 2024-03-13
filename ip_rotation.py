import requests
import configparser
import time
import os
import random

CONFIG_FILE = "config.ini"

def load_config():
    """Loads settings from the configuration file or uses defaults."""
    config = {
        "proxy_file": "proxies.txt",
        "download_url": "https://api.proxyscrape.com/?request=getproxies&proxytype=http",
        "ip_change_interval": 30,
        "download_interval": 300,
        "max_retries": 3
    }

    if os.path.exists(CONFIG_FILE):
        parser = configparser.ConfigParser()
        parser.read(CONFIG_FILE)
        for key in config:
            if parser.has_option('DEFAULT', key):
                value = parser.get('DEFAULT', key)
                config[key] = int(value) if value.isdigit() else value
    return config

def fetch_proxies(config):
    """Downloads new proxies and manages old and new proxy files."""
    download_file = "http_proxies.txt"
    final_file = config["proxy_file"]

    # Remove any existing files
    for file in [download_file, final_file]:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed old file: {file}")

    # Download and rename new proxy file
    try:
        response = requests.get(config["download_url"], timeout=10)
        if response.status_code == 200:
            with open(download_file, "wb") as f:
                f.write(response.content)
            os.rename(download_file, final_file)
            print(f"Downloaded and renamed proxy file to {final_file}")
        else:
            print(f"Proxy download failed with status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Failed to download proxy list: {e}")

def fetch_new_proxy(config):
    """Fetches a new proxy from the file."""
    try:
        with open(config["proxy_file"], 'r') as f:
            proxies = f.readlines()
    except IOError as e:
        print(f"Error reading proxy file: {e}")
        return None

    return random.choice(proxies).strip() if proxies else None

def validate_proxy(proxy):
    """Validates a given proxy by making a test request."""
    test_url = 'http://ipinfo.io/json'
    proxy_dict = {"http": f"http://{proxy}", "https": f"https://{proxy}"}

    try:
        response = requests.get(test_url, proxies=proxy_dict, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def rotate_ip(config):
    """Rotates IP address using a new proxy, applying an exponential backoff strategy."""
    retries = config["max_retries"]
    backoff = 1

    while retries > 0:
        proxy = fetch_new_proxy(config)
        if proxy and validate_proxy(proxy):
            proxy_dict = {"http": f"http://{proxy}", "https": f"https://{proxy}"}
            try:
                response = requests.get("http://ipinfo.io/json", proxies=proxy_dict, timeout=5)
                if response.status_code == 200:
                    print(f"New IP: {response.json()['ip']}")
                    return
                else:
                    print(f"Proxy failed with status code: {response.status_code}")
            except requests.RequestException as e:
                print(f"Proxy request error: {e}")
        time.sleep(backoff)  # Exponential backoff
        backoff *= 2
        retries -= 1

    print("Max retries exceeded. Unable to rotate IP.")

if __name__ == "__main__":
    config = load_config()
    while True:
        start_time = time.time()
        rotate_ip(config)
        if time.time() - start_time >= config["download_interval"]:
            fetch_proxies(config)
        sleep_time = max(0, config["ip_change_interval"] - (time.time() - start_time))
        time.sleep(sleep_time)
