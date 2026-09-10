# This is the base class that every page object inherits from.
# It wraps the raw Selenium calls so our tests don't have to repeat the same boilerplate.

import logging
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

log = logging.getLogger(__name__)

# How long to wait before giving up on finding an element
DEFAULT_TIMEOUT = 15


class BasePage:

    def __init__(self, driver, timeout=DEFAULT_TIMEOUT):
        self.driver = driver
        self.timeout = timeout
        # We ignore stale element errors during waiting — the DOM can flicker
        self._wait = WebDriverWait(
            driver, timeout,
            poll_frequency=0.5,
            ignored_exceptions=[StaleElementReferenceException]
        )

    # ----------------------------------------------------------------
    # Finding elements
    # ----------------------------------------------------------------

    def find_element(self, locator, timeout=None):
        """Wait until the element is visible on screen, then return it."""
        return self._get_wait(timeout).until(EC.visibility_of_element_located(locator))

    def find_elements(self, locator, timeout=None):
        """Return all matching elements (they don't have to be visible)."""
        return self._get_wait(timeout).until(EC.presence_of_all_elements_located(locator))

    def find_clickable(self, locator, timeout=None):
        """Wait until the element can actually be clicked."""
        return self._get_wait(timeout).until(EC.element_to_be_clickable(locator))

    # ----------------------------------------------------------------
    # Interacting with elements
    # ----------------------------------------------------------------

    def click(self, locator, timeout=None):
        """Click an element. If the normal click fails, try a JavaScript click instead."""
        element = self.find_clickable(locator, timeout)
        try:
            element.click()
        except Exception:
            log.warning("Normal click failed on %s — trying JS click", locator)
            self.driver.execute_script("arguments[0].click();", element)

    def send_keys(self, locator, text, clear=True):
        """Type text into a field. Clears the field first by default."""
        element = self.find_element(locator)
        if clear:
            element.clear()
        element.send_keys(text)

    def clear_and_type(self, locator, text):
        """
        Select-all + delete + type. Useful for React inputs where .clear() doesn't work.
        """
        from selenium.webdriver.common.keys import Keys
        element = self.find_element(locator)
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.COMMAND, "a")   # Cmd+A on Mac
        element.send_keys(Keys.BACKSPACE)
        element.send_keys(text)

    # ----------------------------------------------------------------
    # Reading values from the page
    # ----------------------------------------------------------------

    def get_text(self, locator):
        """Return the visible text of an element (trimmed)."""
        return self.find_element(locator).text.strip()

    def get_attribute(self, locator, attribute):
        """Return the value of a specific HTML attribute on an element."""
        return self.find_element(locator).get_attribute(attribute)

    def get_current_url(self):
        return self.driver.current_url

    def get_title(self):
        return self.driver.title

    # ----------------------------------------------------------------
    # Checking what's on screen
    # ----------------------------------------------------------------

    def is_visible(self, locator, timeout=5):
        """Returns True if the element appears within the timeout, False otherwise."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def is_element_present(self, locator, timeout=5):
        """Returns True if the element is in the DOM at all (even if hidden)."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def wait_for_url_contains(self, fragment, timeout=None):
        """Block until the URL includes a specific string (e.g. '/dashboard')."""
        try:
            return self._get_wait(timeout).until(EC.url_contains(fragment))
        except TimeoutException:
            return False

    def wait_for_invisibility(self, locator, timeout=None):
        """Block until an element disappears (e.g. a loading spinner going away)."""
        try:
            return self._get_wait(timeout).until(EC.invisibility_of_element_located(locator))
        except TimeoutException:
            return False

    # ----------------------------------------------------------------
    # Navigation
    # ----------------------------------------------------------------

    def navigate_to(self, url):
        log.info("Going to: %s", url)
        self.driver.get(url)

    def scroll_to(self, locator):
        """Scroll the element into the center of the viewport."""
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)

    # ----------------------------------------------------------------
    # Internal helper
    # ----------------------------------------------------------------

    def _get_wait(self, timeout):
        """Return either the default wait or a one-off wait with a custom timeout."""
        if timeout is None:
            return self._wait
        return WebDriverWait(
            self.driver, timeout,
            poll_frequency=0.5,
            ignored_exceptions=[StaleElementReferenceException]
        )
