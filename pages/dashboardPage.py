# Handles everything on the main dashboard after you log in —
# checking that we landed correctly, going to PIM, and logging out.

import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from pages.basePage import BasePage

log = logging.getLogger(__name__)


class DashboardPage(BasePage):

    # Key elements on the dashboard
    USER_DROPDOWN = (By.CSS_SELECTOR, ".oxd-userdropdown-name")
    LOGOUT_LINK   = (By.XPATH, "//a[normalize-space()='Logout']")
    PIM_MENU      = (By.XPATH, "//span[normalize-space()='PIM']")

    def __init__(self, driver):
        super().__init__(driver)

    def is_loaded(self):
        """
        Are we on the dashboard? We check for the user dropdown in the top-right corner.
        If it's there, we're logged in and the dashboard is up.
        """
        return self.is_visible(self.USER_DROPDOWN, timeout=15)

    def navigate_to_pim(self):
        """Click the PIM menu item in the sidebar and wait for the URL to change."""
        log.info("Going to PIM module")
        pim_element = self.find_element(self.PIM_MENU)
        ActionChains(self.driver).move_to_element(pim_element).click().perform()
        self.wait_for_url_contains("/pim/", timeout=10)

    def logout(self):
        """Click the username dropdown, then hit Logout. Waits for redirect to login page."""
        log.info("Logging out")
        self.click(self.USER_DROPDOWN)
        self.click(self.LOGOUT_LINK)
        self.wait_for_url_contains("/auth/login", timeout=10)
