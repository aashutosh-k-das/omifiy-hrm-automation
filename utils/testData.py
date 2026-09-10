# All the test inputs and expected values live here.
# If the site ever changes credentials or employee names, update this file only.

class TestData:

    # Login credentials for the demo site
    VALID_USERNAME = "Admin"
    VALID_PASSWORD = "admin123"

    # Credentials we know should NOT work
    INVALID_USERNAME = "invalid_user_xyz"
    INVALID_PASSWORD = "invalid_password_xyz"

    # The site URL
    BASE_URL = "https://opensource-demo.orangehrmlive.com"
    LOGIN_URL = f"{BASE_URL}/web/index.php/auth/login"

    # Messages we expect to see on screen
    EXPECTED_ERROR_MESSAGE = "Invalid credentials"
    EXPECTED_REQUIRED_MESSAGE = "Required"

    # Edge cases for security and validation tests
    LONG_STRING_250 = "A" * 250              # way too long for a username
    SPECIAL_CHARS = "!@#$%^&*()_+{}|:\"<>?~`-=[]\\;',./"
    SQL_INJECTION = "' OR '1'='1"           # classic injection attempt
    WHITESPACE_ONLY = "   "                 # just spaces — should still fail

    # Employees we'll create and then look for in the PIM module
    EMPLOYEES = [
        {"first_name": "Aashutosh", "middle_name": "A", "last_name": "Das"},
        {"first_name": "Biki",      "middle_name": "B", "last_name": "Sha"},
        {"first_name": "Pinki",     "middle_name": "C", "last_name": "Mahaset"},
    ]
