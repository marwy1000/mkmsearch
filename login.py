import os
import time
import pickle
from getpass import getpass
import cloudscraper
from bs4 import BeautifulSoup
import oyaml as yaml 
from utils import request_delay

cookie_file = "cardmarket.cookies"
config_file = 'config.yaml'
cardmarket_base_url = "https://www.cardmarket.com/en/Magic"

def login():
    username, password = get_credentials()

    # Create a scraper with a real User-Agent and delay to bypass bot protection
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False},
        delay=20,
    )
    scraper.request_timeout = 30

    scraper.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36"
        )
    })

    # Load persisted cookies (trusted device, session, cf) 
    load_cookies(scraper)

    # Check if already logged in (trusted device path)
    precheck = scraper.get(cardmarket_base_url)
    if "User_Logout" in precheck.text or "Logout" in precheck.text:
        print("Already logged in (trusted device).")
        return scraper

    # Load main page and fetch CSRF token 
    if precheck.status_code != 200:
        raise RuntimeError("Failed to load main page")

    soup = BeautifulSoup(precheck.text, "html.parser")
    token = soup.find("input", {"name": "__cmtkn"})
    if not token:
        raise RuntimeError("Failed to retrieve __cmtkn token")

    # Login attempt
    login_payload = {
        "username": username,
        "userPassword": password,
        "__cmtkn": token["value"],
        "referalPage": "/en/Magic",
    }

    time.sleep(request_delay())
    response = scraper.post(
        f"{cardmarket_base_url}/PostGetAction/User_Login",
        data=login_payload,
        allow_redirects=True,
    )

    # Case 1: redirected to 2FA page
    if "/TwoFactorAuthentication" in response.url:
        print("2FA required.")

        soup = BeautifulSoup(response.text, "html.parser")
        tfa_token = soup.find("input", {"name": "__cmtkn"})
        if not tfa_token:
            raise RuntimeError("Failed to retrieve 2FA token")

        tfa_code = input("Enter 6-digit authenticator code: ").strip()

        scraper.headers.update({
            "X-Requested-With": "XMLHttpRequest",
            "Referer": response.url,
        })

        tfa_payload = {
            "__cmtkn": tfa_token["value"],
            "actionName": "User_Login",
            "code": tfa_code,
            "trustDevice": "1",
        }

        scraper.post(
            f"{cardmarket_base_url}/AjaxAction/GoogleAuthenticator_VerifyCode",
            data=tfa_payload,
        )

        # Finalize login by loading a real page
        verify = scraper.get(cardmarket_base_url)
        if "User_Logout" in verify.text or "Logout" in verify.text:
            save_cookies(scraper)
            print("Login successful (with 2FA).")
            return scraper

        raise RuntimeError("2FA verification failed")

    # Case 2: logged in directly (no 2FA needed)
    verify = scraper.get(cardmarket_base_url)
    if "User_Logout" in verify.text or "Logout" in verify.text:
        save_cookies(scraper)
        print("Login successful (no 2FA).")
        return scraper

    raise RuntimeError("Login failed")


def get_credentials():
    # Check if config.yaml exists
    if os.path.exists(config_file):
        # Read username and password from config.yaml
        with open(config_file, 'r') as file:
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
    with open(config_file, 'w') as file:
        yaml.dump({'username': username, 'password': password}, file)


def load_cookies(scraper):
    if not os.path.exists(cookie_file):
        return False

    with open(cookie_file, "rb") as f:
        scraper.cookies.update(pickle.load(f))
    return True


def save_cookies(scraper):
    with open(cookie_file, "wb") as f:
        pickle.dump(scraper.cookies, f)