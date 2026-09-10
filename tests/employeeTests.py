# End-to-end tests for the PIM (employee management) module.
#
# What we do:
#   1. Log in as Admin
#   2. Add a few employees using the Add Employee form
#   3. Go to the Employee List and search for each one
#   4. Make sure they all show up in the results
#   5. Log out when done

import logging
import pytest

from pages.dashboardPage import DashboardPage
from pages.loginPage import LoginPage
from pages.pimPage import PIMPage
from utils.testData import TestData

log = logging.getLogger(__name__)


# Log in before each test and log out afterwards
@pytest.fixture(autouse=True)
def logged_in_session(browser):
    """
    Set up: log in as Admin and confirm the dashboard loaded.
    Tear down: log out after the test finishes (even if it fails).
    """
    login = LoginPage(browser)
    dashboard = DashboardPage(browser)

    login.load()
    login.login(TestData.VALID_USERNAME, TestData.VALID_PASSWORD)

    assert dashboard.is_loaded(), \
        "Could not log in before the test — dashboard didn't appear."

    yield dashboard  # hand the dashboard to the test

    # Always try to log out, even if something went wrong in the test
    try:
        dashboard.logout()
    except Exception:
        log.warning("Logout after test failed — the browser may have already navigated away.")


class TestEmployeeManagement:

    def test_add_employees_and_find_them_in_the_list(self, browser, logged_in_session):
        """
        Full workflow test:
          - Add all three employees from our test data
          - Search for each one in the Employee List
          - Fail if any of them can't be found
        """
        dashboard = logged_in_session
        pim = PIMPage(browser)

        # --- Step 1: Add everyone ---
        dashboard.navigate_to_pim()

        for person in TestData.EMPLOYEES:
            pim.go_to_add_employee()
            pim.add_employee(
                first_name=person["first_name"],
                last_name=person["last_name"],
                middle_name=person.get("middle_name", ""),
            )
            log.info("Added: %s %s", person["first_name"], person["last_name"])

        # --- Step 2: Search for each one and verify ---
        pim.go_to_employee_list()

        missing = []  # collect all failures before asserting, so we see the full list

        for person in TestData.EMPLOYEES:
            pim.search_by_name(person["first_name"])

            found = pim.is_employee_in_results(
                first_name=person["first_name"],
                last_name=person["last_name"],
            )

            if not found:
                missing.append(f"{person['first_name']} {person['last_name']}")
            else:
                log.info("Verified: %s %s is in the list", person["first_name"], person["last_name"])

        assert not missing, (
            "These employees were added but couldn't be found in the list:\n"
            + "\n".join(f"  - {name}" for name in missing)
        )

    def test_searching_for_nobody_shows_no_results(self, browser, logged_in_session):
        """
        If we search for a name that definitely doesn't exist,
        the table should be empty or show 'No Records Found'.
        """
        dashboard = logged_in_session
        pim = PIMPage(browser)

        dashboard.navigate_to_pim()
        pim.go_to_employee_list()

        # This name is made up — there's no way it exists on the demo site
        pim.search_by_name("ZZZ_Nonexistent_Person_9999")

        assert pim.no_results_found() or pim.result_count() == 0, \
            "Expected no results for a made-up name, but the table showed something."
