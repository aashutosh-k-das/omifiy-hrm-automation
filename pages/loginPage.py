# Everything related to the OrangeHRM login screen lives here.
# This page object handles typing credentials, clicking login, and reading error messages.

import logging
from selenium.webdriver.common.by import By
from pages.basePage import BasePage
from utils.testData import TestData

log = logging.getLogger(__name__)


class LoginPage(BasePage):

    URL = TestData.LOGIN_URL

    # Where things are on the login page
    USERNAME_FIELD    = (By.NAME, "username")
    PASSWORD_FIELD    = (By.NAME, "password")
    LOGIN_BUTTON      = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_ALERT       = (By.CSS_SELECTOR, ".oxd-alert-content-text")
    USERNAME_REQUIRED = (By.XPATH, "//input[@name='username']/parent::div/following-sibling::span")
    PASSWORD_REQUIRED = (By.XPATH, "//input[@name='password']/parent::div/following-sibling::span")
    BRAND_LOGO        = (By.CSS_SELECTOR, ".orangehrm-login-logo")

    def __init__(self, driver):
        super().__init__(driver)

    # ----------------------------------------------------------------
    # Opening the page
    # ----------------------------------------------------------------

    def load(self):
        """Open the login page and wait until the username field is ready."""
        log.info("Opening login page")
        self.navigate_to(self.URL)
        self.find_element(self.USERNAME_FIELD)  # page is ready when this shows up

    # ----------------------------------------------------------------
    # Typing and clicking
    # ----------------------------------------------------------------

    def enter_username(self, username):
        log.debug("Typing username: %s", username)
        self.send_keys(self.USERNAME_FIELD, username)

    def enter_password(self, password):
        log.debug("Typing password")
        self.send_keys(self.PASSWORD_FIELD, password)

    def click_login(self):
        log.info("Clicking the Login button")
        self.click(self.LOGIN_BUTTON)

    def login(self, username, password):
        """Fill in both fields and hit Login. Pass an empty string to leave a field blank."""
        log.info("Logging in as: %s", username)
        if username is not None:
            self.enter_username(username)
        if password is not None:
            self.enter_password(password)
        self.click_login()

    # ----------------------------------------------------------------
    # Reading what's on screen
    # ----------------------------------------------------------------

    def get_error_message(self):
        """Return the red error text shown after a bad login attempt."""
        return self.get_text(self.ERROR_ALERT)

    def get_username_required_message(self):
        """Return the 'Required' hint that appears below the username field."""
        return self.get_text(self.USERNAME_REQUIRED)

    def get_password_required_message(self):
        """Return the 'Required' hint that appears below the password field."""
        return self.get_text(self.PASSWORD_REQUIRED)

    def get_password_input_type(self):
        """Check the type attribute of the password box — should be 'password', not 'text'."""
        return self.get_attribute(self.PASSWORD_FIELD, "type")

    def is_login_page_visible(self):
        """Quick check: is the OrangeHRM logo visible? If yes, we're on the login page."""
        return self.is_visible(self.BRAND_LOGO, timeout=10)
