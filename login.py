import os
import time
from getpass import getpass
import cloudscraper
from bs4 import BeautifulSoup
import oyaml as yaml 
from utils import request_delay

CONFIG_FILE = 'config.yaml'


def login():
    username, password = get_credentials()

    # Create a scraper with a real User-Agent and delay to bypass bot protection
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        },
        delay=20  # Helps bypass Cloudflare rate limits
    )

    scraper.request_timeout = 30  # 30 seconds per request


    scraper.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36' #'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/537.36'
    })



    main_page_url = "https://www.cardmarket.com/en/Magic"
    main_page_response = scraper.get(main_page_url)

    if main_page_response.status_code != 200:
        print(f"Failed to load the main page. Status Code: {main_page_response.status_code}")
        print(f"Response Text (first 500 chars): {main_page_response.text[:500]}")
        print("Possible causes: Cloudflare protection, IP ban, or incorrect headers.")
        exit(1)

    soup = BeautifulSoup(main_page_response.text, "html.parser")
    token_element = soup.find("input", {"name": "__cmtkn"})

    if not token_element:
        print("Failed to retrieve __cmtkn token. Dumping first 500 characters of page:")
        print(main_page_response.text[:500])
        exit(1)

    token_value = token_element.get("value")

    login_url = "https://www.cardmarket.com/en/Magic/PostGetAction/User_Login"
    payload = {
        "username": username,
        "userPassword": password,
        "__cmtkn": token_value,
        "referalPage": "/en/Magic"
    }
    time.sleep(request_delay())
    response = scraper.post(login_url, data=payload)

    if "Logout" in response.text:  
        print("Login successful!")
        return scraper

    print("Login failed. Check your credentials.")
    print(f"Response Text (first 500 chars): {response.text[:500]}")
    exit(1)


def get_credentials():
    # Check if config.yaml exists
    if os.path.exists(CONFIG_FILE):
        # Read username and password from config.yaml
        with open(CONFIG_FILE, 'r') as file:
            config = yaml.safe_load(file)

        # Return credentials if found
        if 'username' in config and 'password' in config:
            return config['username'], config['password']  # No need to save back

    # If config.yaml doesn't exist or is missing credentials, prompt the user
    username = input("Enter username: ")
    password = getpass("Enter password: ")
    save_credentials(username, password)

    return username, password  # Indicate credentials should be saved back

def save_credentials(username, password):
    # Write username and password to config.yaml
    with open(CONFIG_FILE, 'w') as file:
        yaml.dump({'username': username, 'password': password}, file)
