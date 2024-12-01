import os
from getpass import getpass
import cloudscraper
from bs4 import BeautifulSoup
import oyaml as yaml 

CONFIG_FILE = 'config.yaml'

def login():

    # Prompt user for credentials or get it from the config file
    username, password, needs_saving = get_credentials()


    # Set up the scraper session
    # scraper = cloudscraper.create_scraper() 
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        }
    )

    # Step 1: Get the main page to fetch the dynamic __cmtkn token
    main_page_url = "https://www.cardmarket.com/en/Magic"
    main_page_response = scraper.get(main_page_url)

    # Check if the main page loaded correctly
    if main_page_response.status_code != 200:
        print("Failed to load the main page.")
        exit(1)

    # Step 2: Parse the HTML to extract the __cmtkn token
    soup = BeautifulSoup(main_page_response.text, "html.parser")
    token_element = soup.find("input", {"name": "__cmtkn"})

    if not token_element:
        print("Failed to retrieve __cmtkn token.")
        return

    # Extract the token value
    token_value = token_element.get("value")
    # Step 3: Prepare the login POST request
    login_url = "https://www.cardmarket.com/en/Magic/PostGetAction/User_Login"
    payload = {
        "username": username,
        "userPassword": password,
        "__cmtkn": token_value,
        "referalPage": "/en/Magic"
    }

    # Send the login request
    response = scraper.post(login_url, data=payload)

    # Step 4: Check the login response for success
    if "Logout" in response.text:  # Adjust based on actual response content
        print("Login successful!")
        if needs_saving:
            save_credentials(username, password)
        return scraper

    print("Login failed. Check your credentials.")
    exit(1)


def get_credentials():
    # Check if config.yaml exists
    if os.path.exists(CONFIG_FILE):
        # Read username and password from config.yaml
        with open(CONFIG_FILE, 'r') as file:
            config = yaml.safe_load(file)

        # Return credentials if found
        if 'username' in config and 'password' in config:
            return config['username'], config['password'], False  # No need to save back

    # If config.yaml doesn't exist or is missing credentials, prompt the user
    username = input("Enter username: ")
    password = getpass("Enter password: ")

    return username, password, True  # Indicate credentials should be saved back

def save_credentials(username, password):
    # Write username and password to config.yaml
    with open(CONFIG_FILE, 'w') as file:
        yaml.dump({'username': username, 'password': password}, file)
