# Login page tests for OrangeHRM.
# We test the happy path, validation errors, and a few known bugs.
# The known bugs are marked xfail — they won't cause the test run to fail,
# but they document real issues we found on the site.

import pytest
from pages.loginPage import LoginPage
from pages.dashboardPage import DashboardPage
from utils.testData import TestData


# Before every test: open a fresh login page
@pytest.fixture(autouse=True)
def login_page(browser):
    """Load the login page and hand it to the test."""
    page = LoginPage(browser)
    page.load()
    return page


@pytest.fixture()
def dashboard(browser):
    return DashboardPage(browser)


class TestLogin:

    # ----------------------------------------------------------------
    # Happy path — these should all work correctly
    # ----------------------------------------------------------------

    def test_01_valid_login_redirects_to_dashboard(self, login_page, dashboard):
        """Correct username + password should land us on the dashboard."""
        login_page.login(TestData.VALID_USERNAME, TestData.VALID_PASSWORD)
        assert dashboard.is_loaded(), "Expected the dashboard to load after a valid login."
        dashboard.logout()

    def test_02_invalid_password_shows_error(self, login_page):
        """Wrong password should show 'Invalid credentials', not crash or redirect."""
        login_page.login(TestData.VALID_USERNAME, "wrong_password_xyz")
        error = login_page.get_error_message()
        assert error == TestData.EXPECTED_ERROR_MESSAGE, \
            f"Expected '{TestData.EXPECTED_ERROR_MESSAGE}' but got '{error}'"

    def test_03_invalid_username_shows_error(self, login_page):
        """A username that doesn't exist should also show 'Invalid credentials'."""
        login_page.login(TestData.INVALID_USERNAME, TestData.VALID_PASSWORD)
        error = login_page.get_error_message()
        assert error == TestData.EXPECTED_ERROR_MESSAGE, \
            f"Expected '{TestData.EXPECTED_ERROR_MESSAGE}' but got '{error}'"

    def test_04_both_fields_wrong_shows_error(self, login_page):
        """When both username and password are wrong, the error message should still appear."""
        login_page.login(TestData.INVALID_USERNAME, TestData.INVALID_PASSWORD)
        assert login_page.get_error_message() == TestData.EXPECTED_ERROR_MESSAGE

    # ----------------------------------------------------------------
    # Field validation — what happens when fields are left empty
    # ----------------------------------------------------------------

    def test_05_empty_username_shows_required(self, login_page):
        """Leaving the username blank and clicking Login should show 'Required' underneath it."""
        login_page.login("", TestData.VALID_PASSWORD)
        msg = login_page.get_username_required_message()
        assert msg == TestData.EXPECTED_REQUIRED_MESSAGE, \
            f"Expected 'Required' under username but got '{msg}'"

    def test_06_empty_password_shows_required(self, login_page):
        """Leaving the password blank should show 'Required' underneath it."""
        login_page.login(TestData.VALID_USERNAME, "")
        msg = login_page.get_password_required_message()
        assert msg == TestData.EXPECTED_REQUIRED_MESSAGE, \
            f"Expected 'Required' under password but got '{msg}'"

    def test_07_both_fields_empty_shows_required_on_both(self, login_page):
        """Submitting a completely empty form should flag both fields as Required."""
        login_page.login("", "")
        assert login_page.get_username_required_message() == TestData.EXPECTED_REQUIRED_MESSAGE
        assert login_page.get_password_required_message() == TestData.EXPECTED_REQUIRED_MESSAGE

    # ----------------------------------------------------------------
    # Security and UI checks
    # ----------------------------------------------------------------

    def test_08_password_is_hidden(self, login_page):
        """The password field should have type='password' so the text is masked."""
        input_type = login_page.get_password_input_type()
        assert input_type == "password", \
            f"Password field type is '{input_type}' — the password might be visible!"

    def test_09_page_title_is_correct(self, login_page):
        """The browser tab title should mention OrangeHRM."""
        title = login_page.get_title()
        assert "OrangeHRM" in title, f"Unexpected page title: '{title}'"

    def test_10_login_url_is_correct(self, login_page):
        """The URL should include /auth/login when we're on the login page."""
        url = login_page.get_current_url()
        assert "/auth/login" in url, f"Unexpected URL: '{url}'"

    # ----------------------------------------------------------------
    # Known bugs — documented as xfail so they don't break CI
    # ----------------------------------------------------------------

    @pytest.mark.xfail(
        strict=False,
        reason="BUG-001: Typing 'admin' (lowercase) still logs in — username should be case-sensitive."
    )
    def test_11_username_should_be_case_sensitive(self, login_page):
        """'admin' should NOT log in as 'Admin' — but it does. That's the bug."""
        login_page.login("admin", TestData.VALID_PASSWORD)
        error = login_page.get_error_message()
        assert error == TestData.EXPECTED_ERROR_MESSAGE, \
            "Lowercase 'admin' was accepted — the site doesn't check case."

    @pytest.mark.xfail(
        strict=False,
        reason="BUG-002: No lockout or CAPTCHA after 10 failed login attempts. Brute-force risk."
    )
    def test_12_repeated_failures_should_trigger_lockout(self, login_page):
        """After 10 wrong attempts, we'd expect a CAPTCHA or lockout. We never get one."""
        for _ in range(10):
            login_page.login(TestData.VALID_USERNAME, "wrong_password")
            login_page.load()
        error = login_page.get_error_message()
        assert error != TestData.EXPECTED_ERROR_MESSAGE, \
            "Still getting the normal error message after 10 failed attempts — no lockout."

    @pytest.mark.xfail(
        strict=False,
        reason="BUG-003: A 250-character username goes straight to the server. Should fail inline."
    )
    def test_13_very_long_username_should_be_rejected_early(self, login_page):
        """A 250-char username should show a length error on screen, not hit the backend."""
        login_page.login(TestData.LONG_STRING_250, "wrong_password")
        error = login_page.get_error_message()
        assert error != TestData.EXPECTED_ERROR_MESSAGE, \
            "The app sent a 250-char username to the server — no client-side length check."

    @pytest.mark.xfail(
        strict=False,
        reason="BUG-004: SQL injection in the username field — should be blocked."
    )
    def test_14_sql_injection_should_not_bypass_login(self, login_page, dashboard):
        """A classic SQL injection string in the username should NOT log us in."""
        login_page.login(TestData.SQL_INJECTION, TestData.VALID_PASSWORD)
        assert not dashboard.is_loaded(), \
            "SQL injection bypassed authentication — this is a critical security issue!"
