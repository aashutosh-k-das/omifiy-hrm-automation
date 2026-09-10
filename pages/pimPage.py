# Everything for the PIM (Personnel Information Management) module.
# Covers two main areas: the "Add Employee" form and the "Employee List" search.

import logging
import random
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from pages.basePage import BasePage

log = logging.getLogger(__name__)


class PIMPage(BasePage):

    # Sidebar tabs inside PIM
    ADD_EMPLOYEE_TAB  = (By.XPATH, "//a[normalize-space()='Add Employee']")
    EMPLOYEE_LIST_TAB = (By.XPATH, "//a[normalize-space()='Employee List']")

    # Fields on the Add Employee form
    FIRST_NAME  = (By.NAME, "firstName")
    MIDDLE_NAME = (By.NAME, "middleName")
    LAST_NAME   = (By.NAME, "lastName")
    EMPLOYEE_ID = (By.XPATH, "//label[normalize-space()='Employee Id']/../following-sibling::div//input")
    SAVE_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    SUCCESS_TOAST = (By.CSS_SELECTOR, ".oxd-toast-content--success")

    # Fields and results on the Employee List page
    NAME_SEARCH_BOX   = (By.XPATH, "//label[normalize-space()='Employee Name']/../following-sibling::div//input")
    SEARCH_BUTTON     = (By.CSS_SELECTOR, "button[type='submit']")
    RESET_BUTTON      = (By.CSS_SELECTOR, "button[type='reset']")
    TABLE_ROWS        = (By.CSS_SELECTOR, ".oxd-table-body .oxd-table-row")
    LOADING_SPINNER   = (By.CSS_SELECTOR, ".oxd-loading-spinner")
    NO_RECORDS_FOUND  = (By.XPATH, "//span[normalize-space()='No Records Found']")
    AUTOCOMPLETE_ITEM = (By.CSS_SELECTOR, ".oxd-autocomplete-option span")

    def __init__(self, driver):
        super().__init__(driver)

    # ----------------------------------------------------------------
    # Moving around inside the PIM module
    # ----------------------------------------------------------------

    def go_to_add_employee(self):
        """Click 'Add Employee' and wait for the form to appear."""
        log.info("Opening Add Employee form")
        self.click(self.ADD_EMPLOYEE_TAB)
        self.find_element(self.FIRST_NAME)  # form is ready when the name field shows up

    def go_to_employee_list(self):
        """Click 'Employee List' and wait for the search bar to load."""
        log.info("Opening Employee List")
        self.click(self.EMPLOYEE_LIST_TAB)
        self.find_element(self.NAME_SEARCH_BOX)
        self._wait_for_loading()

    # ----------------------------------------------------------------
    # Adding a new employee
    # ----------------------------------------------------------------

    def add_employee(self, first_name, last_name, middle_name=""):
        """
        Fill in the Add Employee form and save it.
        We generate a random Employee ID each time to avoid conflicts on the shared demo site.
        Returns the ID that was assigned.
        """
        log.info("Adding employee: %s %s %s", first_name, middle_name, last_name)

        self.send_keys(self.FIRST_NAME, first_name)
        if middle_name:
            self.send_keys(self.MIDDLE_NAME, middle_name)
        self.send_keys(self.LAST_NAME, last_name)

        # Give the employee a random ID so we don't clash with existing records
        random_id = str(random.randint(100_000, 999_999))
        self._set_employee_id(random_id)

        self.click(self.SAVE_BUTTON)

        # Check for the green success toast (but don't crash if it's too fast to catch)
        try:
            self.find_element(self.SUCCESS_TOAST, timeout=10)
            log.info("Employee saved! ID: %s", random_id)
        except Exception:
            log.warning("Didn't catch the success toast — the save might still have worked.")

        return random_id

    def _set_employee_id(self, emp_id):
        """
        The Employee ID field is React-controlled so .clear() doesn't work on it.
        We use Ctrl/Cmd+A then Backspace to wipe it out before typing the new value.
        """
        field = self.find_element(self.EMPLOYEE_ID)
        field.send_keys(Keys.CONTROL, "a")
        field.send_keys(Keys.COMMAND, "a")   # Mac needs Cmd
        field.send_keys(Keys.BACKSPACE)
        time.sleep(0.3)
        field.send_keys(emp_id)

    # ----------------------------------------------------------------
    # Searching for employees
    # ----------------------------------------------------------------

    def reset_filters(self):
        """Click the Reset button to clear whatever was searched before."""
        try:
            self.click(self.RESET_BUTTON, timeout=5)
            self._wait_for_loading()
        except Exception:
            log.debug("No reset button found — skipping reset.")

    def search_by_name(self, first_name):
        """
        Type a name into the search box, pick the first autocomplete suggestion,
        then hit Search and wait for results to load.
        """
        log.info("Searching for: %s", first_name)
        self.reset_filters()

        # Clear the React autocomplete field manually
        field = self.find_element(self.NAME_SEARCH_BOX)
        field.send_keys(Keys.CONTROL, "a")
        field.send_keys(Keys.COMMAND, "a")
        field.send_keys(Keys.BACKSPACE)
        field.send_keys(first_name)

        # The demo site needs a moment to show autocomplete suggestions
        time.sleep(2)

        try:
            first_suggestion = self.find_element(self.AUTOCOMPLETE_ITEM, timeout=8)
            first_suggestion.click()
            time.sleep(1)  # let React update the input field
        except Exception:
            log.debug("No autocomplete dropdown appeared — searching without it.")

        self.click(self.SEARCH_BUTTON)
        self._wait_for_loading()
        time.sleep(2)  # give the demo site extra time to render results

    # ----------------------------------------------------------------
    # Checking search results
    # ----------------------------------------------------------------

    def is_employee_in_results(self, first_name, last_name):
        """
        Look through the result table and return True if any row contains
        both the first and last name we're looking for.

        We re-fetch each row fresh instead of reusing cached references
        because React can re-render the table between iterations.
        """
        try:
            rows = self.find_elements(self.TABLE_ROWS, timeout=10)
            total_rows = len(rows)
        except Exception:
            log.warning("No rows in the table at all.")
            return False

        fn = first_name.lower()
        ln = last_name.lower()

        for i in range(total_rows):
            try:
                # Re-query all rows each time to get a fresh reference
                fresh_rows = self.driver.find_elements(*self.TABLE_ROWS)
                if i >= len(fresh_rows):
                    break
                row_text = fresh_rows[i].text.lower()
                if fn in row_text and ln in row_text:
                    log.info("Found in list: %s %s", first_name, last_name)
                    return True
            except Exception as e:
                log.debug("Row %d went stale, skipping: %s", i, e)
                continue

        log.warning("Not found in list: %s %s", first_name, last_name)
        return False

    def no_results_found(self):
        """Returns True when the 'No Records Found' message is on screen."""
        return self.is_visible(self.NO_RECORDS_FOUND, timeout=5)

    def result_count(self):
        """How many rows are currently showing in the table?"""
        try:
            return len(self.find_elements(self.TABLE_ROWS, timeout=5))
        except Exception:
            return 0

    # ----------------------------------------------------------------
    # Internal helper
    # ----------------------------------------------------------------

    def _wait_for_loading(self):
        """Wait until the spinning loader disappears before moving on."""
        self.wait_for_invisibility(self.LOADING_SPINNER, timeout=15)
