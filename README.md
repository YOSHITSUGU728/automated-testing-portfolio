# Automated Testing Portfolio
QA Automation Test Scripts using Python & Selenium

## Projects

### 1. Regression Test - Sign-up & Login Flow
Automated regression test covering user registration, logout, login, and logout flow.

### 2. 404 Error Detection & Screenshot Tool
Automated tool to detect 404 errors on websites and capture screenshots as evidence.

### 3. Form Validation Test — Login Page (35 Test Cases)
Automated form validation test suite covering 35 input patterns on a login page, including full-width/Japanese characters, boundary values, SQL injection, and XSS attempts. Screenshots are automatically captured on failure. Results exported to CSV and JSON.

### 4. E-Commerce Checkout Flow Automation Test (SauceDemo)
Automated end-to-end test suite covering a full e-commerce purchasing flow including login validation, product listing, add to cart, checkout, order summary & price calculation, order completion, and logout. 10 test cases with both positive and negative scenarios. Screenshots automatically captured at each step. 100% pass rate achieved.

### 5. Authentication Flow API Test (Restful Booker)

📄 `api/test_auth_flow_api.py`

Automated API test suite covering a full authentication flow including login, token acquisition, booking creation, update, deletion, and unauthorized access rejection. 6 test cases using Playwright APIRequestContext (Python).

| TC | Test Name | Description |
|---|---|---|
| TC01 | Login Success | Verify valid token is returned with correct credentials |
| TC02 | Login Failure | Verify no token is issued with wrong password |
| TC03 | Create Booking | Verify booking can be created with valid token (POST) |
| TC04 | Update Booking | Verify booking can be updated with valid token (PUT) |
| TC05 | Delete Booking | Verify booking can be deleted with valid token (DELETE) |
| TC06 | Unauthorized Access | Verify request is rejected without token (403 Forbidden) |

- ✅ 6/6 test cases passed
- 🔐 Security test included (TC06 - 403 Forbidden verification)
- ⚡ API-level testing without browser (5 seconds execution)
- 📊 HTML report auto-generated via pytest-html

---

## Technologies
- Python
- Selenium
- Playwright
- pytest

## Requirements
- Python 3.x
- Selenium 4.x
- Chrome WebDriver

## Contact
- Upwork: https://upwork.com/freelancers/~01a89098eaefc3fe0b
- LinkedIn: https://www.linkedin.com/in/yoshitsugu-baba-68b8a0375
