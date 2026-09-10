# omifiy-hrm-automation 🤖

Automated test suite for [OrangeHRM](https://opensource-demo.orangehrmlive.com) built with **Python + Selenium + pytest**.
Uses the **Page Object Model (POM)** pattern so tests are clean, readable, and easy to maintain.

---

## 📂 Project Structure

```
omifiy-hrm-automation/
├── pages/
│   ├── basePage.py          # Shared Selenium helpers (click, type, wait, etc.)
│   ├── loginPage.py         # Login screen interactions
│   ├── dashboardPage.py     # Dashboard navigation & logout
│   └── pimPage.py           # Add Employee form & Employee List search
├── tests/
│   ├── loginTests.py        # 14 tests covering login + known bugs
│   └── employeeTests.py     # End-to-end employee add & verify workflow
├── utils/
│   └── testData.py          # All test credentials, URLs, and employee data
├── screenshots/             # Auto-saved on test failure
├── conftest.py              # Browser setup, fixtures & screenshot hook
├── pytest.ini               # pytest configuration
└── requirements.txt         # Python dependencies
```

---

## 🚀 Setup

**1. Install Python 3.8+** (if not already installed)

**2. Clone the repo**
```bash
git clone https://github.com/aashutosh-k-das/omifiy-hrm-automation.git
cd omifiy-hrm-automation
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

Chrome is managed automatically by Selenium 4 — no manual chromedriver needed.

---

## ▶️ Running Tests

```bash
# Run all 16 tests
python3 -m pytest tests/ -v -s

# Login tests only (14 tests)
python3 -m pytest tests/loginTests.py -v -s

# Employee management tests only (2 tests)
python3 -m pytest tests/employeeTests.py -v -s

# Run without a browser window (headless)
HEADLESS=1 python3 -m pytest tests/ -v -s

# Generate an HTML report
python3 -m pytest tests/ -v -s --html=report.html
```

---

## 🧪 Test Coverage

### Login Tests (`loginTests.py`) — 14 tests

| # | Test | Type |
|---|------|------|
| 01 | Valid login → dashboard loads | ✅ Normal |
| 02 | Wrong password → error message | ✅ Normal |
| 03 | Invalid username → error message | ✅ Normal |
| 04 | Both fields wrong → error message | ✅ Normal |
| 05 | Empty username → Required hint | ✅ Normal |
| 06 | Empty password → Required hint | ✅ Normal |
| 07 | Both fields empty → Required on both | ✅ Normal |
| 08 | Password field is masked | ✅ Normal |
| 09 | Page title contains OrangeHRM | ✅ Normal |
| 10 | URL contains /auth/login | ✅ Normal |
| 11 | Username is not case-sensitive | ⚠️ Bug |
| 12 | No rate limiting after 10 failures | ⚠️ Bug |
| 13 | No character limit on username | ⚠️ Bug |
| 14 | SQL injection doesn't bypass auth | ⚠️ Bug |

### Employee Tests (`employeeTests.py`) — 2 tests

| # | Test | Type |
|---|------|------|
| 01 | Add 3 employees + verify each in list | ✅ E2E |
| 02 | Search for non-existent name → no results | ✅ Normal |

---

## 🐛 Known Bugs Found

These are documented as `xfail` tests — they won't break the CI pipeline but they record real issues:

1. **Username is not case-sensitive** — `admin` logs in the same as `Admin`. Authentication should be strict.
2. **No rate limiting** — 10+ failed login attempts produce no CAPTCHA or lockout. Brute-force risk.
3. **No character limit** — A 250-character username gets sent to the backend with no inline validation.
4. **SQL injection not blocked client-side** — The injection string is passed through without sanitisation.

---

## 🛠️ Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.8+ | Language |
| Selenium | 4.21.0 | Browser automation |
| pytest | 8.2.2 | Test runner |
| pytest-html | 4.1.1 | HTML reports |
| webdriver-manager | 4.0.1 | Auto chromedriver management |

---

## 📸 Screenshots

Failure screenshots are automatically saved to the `screenshots/` folder and embedded in HTML reports.
