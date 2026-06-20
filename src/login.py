import os
import time
import pickle
from getpass import getpass
import cloudscraper
from bs4 import BeautifulSoup
import oyaml as yaml
from src.utils import request_delay

cookie_file = "cardmarket.cookies"
config_file = "config.yaml"
cardmarket_base_url = "https://www.cardmarket.com/en/Magic"


def login(force=False):
    username, password = get_credentials()

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

    # Load cookies first
    load_cookies(scraper)

    # Validate session before trusting cookies
    if not force and validate_session(scraper):
        print("Already logged in (valid session).")
        return scraper

    # Clear stale cookies
    scraper.cookies.clear()

    # Load login page
    precheck = scraper.get(cardmarket_base_url)

    if precheck.status_code != 200:
        raise RuntimeError(f"Failed to load main page: {precheck.status_code}")

    soup = BeautifulSoup(precheck.text, "html.parser")
    token = soup.find("input", {"name": "__cmtkn"})

    if not token:
        raise RuntimeError("Missing CSRF token — page structure changed or blocked")

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

    # 2FA FLOW
    if "/TwoFactorAuthentication" in response.url:
        print("2FA required.")

        soup = BeautifulSoup(response.text, "html.parser")
        tfa_token = soup.find("input", {"name": "__cmtkn"})

        if not tfa_token:
            raise RuntimeError("Missing 2FA CSRF token")

        tfa_code = input("Enter 6-digit authenticator code: ").strip()

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

        if not validate_session(scraper):
            raise RuntimeError("2FA failed — session not authenticated")

        save_cookies(scraper)
        print("Login successful (2FA).")
        return scraper

    # NORMAL LOGIN VALIDATION
    if not validate_session(scraper):
        raise RuntimeError("Login failed — session not established")

    save_cookies(scraper)
    print("Login successful.")
    return scraper


def validate_session(scraper):
    """
    Minimal, robust session validation.
    No HTML parsing logic beyond necessity.
    """

    try:
        # Use a lightweight endpoint that requires auth
        resp = scraper.get(
            f"{cardmarket_base_url}/Account/Statistics",
            allow_redirects=False,
            timeout=20
        )

        # If redirected → not authenticated
        if resp.status_code in (301, 302, 303, 307, 308):
            return False

        # Hard failure cases
        if resp.status_code != 200:
            return False

        # If login page is served → not authenticated
        if "userPassword" in resp.text:
            return False

        return True

    except Exception:
        return False


def get_credentials():
    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            config = yaml.safe_load(file)

        if "username" in config and "password" in config:
            return config["username"], config["password"]

    username = input("Enter username: ")
    password = getpass("Enter password: ")
    save_credentials(username, password)

    return username, password


def save_credentials(username, password):
    with open(config_file, "w") as file:
        yaml.dump({"username": username, "password": password}, file)


def load_cookies(scraper):
    if not os.path.exists(cookie_file):
        return False

    try:
        with open(cookie_file, "rb") as f:
            scraper.cookies.update(pickle.load(f))
        return True
    except Exception:
        return False


def save_cookies(scraper):
    with open(cookie_file, "wb") as f:
        pickle.dump(scraper.cookies, f)