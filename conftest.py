# Browser setup and failure-screenshot hook for the entire test session.
# One Chrome window is shared across all tests — it opens at the start and closes at the end.

import logging
import os
from datetime import datetime

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Set up logging so we can see INFO messages in the terminal as tests run
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-7s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

SCREENSHOT_DIR = "screenshots"


def build_chrome_options():
    """
    Set up Chrome the way we want it.
    To run without a visible window, set the HEADLESS environment variable:
        HEADLESS=1 pytest
    """
    opts = Options()

    if os.getenv("HEADLESS", "").strip() in ("1", "true", "yes"):
        log.info("Running in headless mode (no browser window)")
        opts.add_argument("--headless=new")

    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--log-level=3")  # silence Chrome's own console output

    return opts


@pytest.fixture(scope="session")
def browser():
    """
    This fixture starts Chrome before the first test and keeps it open
    until the very last test finishes — then it closes it.

    We also attach the driver to pytest itself so our screenshot hook
    can grab it without needing a fixture parameter.
    """
    log.info("Starting Chrome")
    driver = webdriver.Chrome(options=build_chrome_options())
    driver.implicitly_wait(0)   # we use explicit waits everywhere — no implicit waits

    pytest.driver = driver      # make the driver available to the screenshot hook below

    yield driver

    log.info("Closing Chrome")
    driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    After each test, if it FAILED (and it wasn't an expected failure),
    take a screenshot and attach it to the HTML report.
    """
    pytest_html = item.config.pluginmanager.getplugin("html")
    outcome = yield
    report = outcome.get_result()
    extras = getattr(report, "extras", [])

    if report.when in ("call", "setup"):
        is_expected_failure = hasattr(report, "wasxfail")
        should_screenshot = (report.skipped and is_expected_failure) or \
                            (report.failed and not is_expected_failure)

        if should_screenshot:
            driver = getattr(pytest, "driver", None)
            if driver:
                os.makedirs(SCREENSHOT_DIR, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = os.path.join(SCREENSHOT_DIR, f"{item.name}_{timestamp}.png")

                try:
                    driver.save_screenshot(screenshot_path)
                    log.info("Screenshot saved: %s", screenshot_path)
                except Exception as e:
                    log.warning("Could not take screenshot: %s", e)

                # Embed the screenshot in the HTML report if one is being generated
                if pytest_html is not None:
                    html = (
                        f'<div><img src="../{screenshot_path}" alt="failure screenshot" '
                        f'style="width:600px;" onclick="window.open(this.src)"/></div>'
                    )
                    extras.append(pytest_html.extras.html(html))

    report.extras = extras
