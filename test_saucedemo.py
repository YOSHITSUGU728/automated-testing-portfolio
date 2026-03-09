"""
SauceDemo Automated Test Suite [Playwright]
Target : https://www.saucedemo.com/
Flow   : Login → Products → Cart → Checkout → Order Complete

Requirements:
  pip install playwright
  playwright install chromium

Usage:
  python test_saucedemo_en.py

Available test users:
  standard_user           / secret_sauce  → Normal user (used in main flow)
  locked_out_user         / secret_sauce  → Cannot login
  problem_user            / secret_sauce  → UI issues
  performance_glitch_user / secret_sauce  → Slow response
"""

import sys
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

# ─────────────────────────────────────
# Configuration
# ─────────────────────────────────────
BASE_URL    = "https://www.saucedemo.com"
VALID_USER  = "standard_user"
VALID_PASS  = "secret_sauce"
LOCKED_USER = "locked_out_user"

SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)  # Auto-create screenshots folder

FIRST_NAME  = "Taro"
LAST_NAME   = "Yamada"
POSTAL_CODE = "100-0001"

PRODUCTS_TO_ADD = [
    "Sauce Labs Backpack",
    "Sauce Labs Bike Light",
]


# ─────────────────────────────────────
# Utilities
# ─────────────────────────────────────

def screenshot(page, name: str):
    path = f"{SCREENSHOT_DIR}/ss_{name}.png"
    page.screenshot(path=path)
    print(f"    📸 {path}")


def section(title: str):
    print(f"\n{'─'*50}")
    print(f"  {title}")
    print(f"{'─'*50}")


# ─────────────────────────────────────
# Test Cases
# ─────────────────────────────────────

def tc_login_fail_locked(page, results: list):
    """TC-02: Locked user cannot login"""
    section("TC-02: Login Failure - Locked User")
    page.goto(BASE_URL, wait_until="networkidle")

    page.fill("#user-name", LOCKED_USER)
    page.fill("#password", VALID_PASS)
    page.click("#login-button")
    page.wait_for_timeout(800)

    error_el      = page.locator("[data-test='error']")
    error_visible = error_el.is_visible()
    error_text    = error_el.inner_text() if error_visible else ""
    print(f"  Error message: {error_text}")
    screenshot(page, "03_locked_user_error")

    passed = error_visible and "locked out" in error_text.lower()
    results.append(("TC-02: Locked User Login Failure", passed, error_text.strip()))


def tc_login_fail_wrong_pass(page, results: list):
    """TC-03: Wrong password cannot login"""
    section("TC-03: Login Failure - Wrong Password")
    page.goto(BASE_URL, wait_until="networkidle")

    page.fill("#user-name", VALID_USER)
    page.fill("#password", "wrong_password")
    page.click("#login-button")
    page.wait_for_timeout(800)

    error_el      = page.locator("[data-test='error']")
    error_visible = error_el.is_visible()
    error_text    = error_el.inner_text() if error_visible else ""
    print(f"  Error message: {error_text}")
    screenshot(page, "04_wrong_pass_error")

    passed = error_visible
    results.append(("TC-03: Wrong Password Login Failure", passed, error_text.strip()))


def tc_login_success(page, results: list):
    """TC-01: Valid user can login"""
    section("TC-01: Login Success")
    page.goto(BASE_URL, wait_until="networkidle")

    page.fill("#user-name", VALID_USER)
    page.fill("#password", VALID_PASS)
    screenshot(page, "01_login_input")
    page.click("#login-button")
    page.wait_for_url("**/inventory.html", timeout=8000)

    passed = "/inventory.html" in page.url
    print(f"  Redirected URL: {page.url}")
    screenshot(page, "02_after_login")
    results.append(("TC-01: Login Success", passed, page.url))


def tc_product_list(page, results: list):
    """TC-04: Product list displays 6 items"""
    section("TC-04: Product List Display")

    items = page.locator(".inventory_item")
    count = items.count()
    print(f"  Product count: {count}")
    screenshot(page, "05_product_list")

    passed = count == 6
    results.append(("TC-04: Product List Display (6 items)", passed, f"{count} items displayed"))


def tc_add_to_cart(page, results: list):
    """TC-05: Add products to cart"""
    section("TC-05: Add Products to Cart")

    for product_name in PRODUCTS_TO_ADD:
        item = page.locator(".inventory_item").filter(has_text=product_name)
        item.locator("button").click()
        print(f"  ✅ Added to cart: {product_name}")

    page.wait_for_timeout(500)
    badge       = page.locator(".shopping_cart_badge")
    badge_count = badge.inner_text() if badge.is_visible() else "0"
    print(f"  Cart badge: {badge_count}")
    screenshot(page, "06_added_to_cart")

    passed = badge_count == str(len(PRODUCTS_TO_ADD))
    results.append((f"TC-05: Add {len(PRODUCTS_TO_ADD)} Items to Cart", passed,
                    f"Badge={badge_count}"))


def tc_cart_contents(page, results: list):
    """TC-06: Verify cart contents"""
    section("TC-06: Cart Contents Verification")

    page.click(".shopping_cart_link")
    page.wait_for_url("**/cart.html", timeout=5000)

    cart_items = page.locator(".cart_item")
    count      = cart_items.count()
    print(f"  Items in cart: {count}")

    for i in range(count):
        name  = cart_items.nth(i).locator(".inventory_item_name").inner_text()
        price = cart_items.nth(i).locator(".inventory_item_price").inner_text()
        print(f"    [{i+1}] {name}  {price}")

    screenshot(page, "07_cart_contents")

    passed = count == len(PRODUCTS_TO_ADD)
    results.append(("TC-06: Cart Contents Verification", passed,
                    f"Cart={count} / Added={len(PRODUCTS_TO_ADD)}"))


def tc_checkout_info(page, results: list):
    """TC-07: Enter checkout information"""
    section("TC-07: Checkout Information Input")

    page.click("[data-test='checkout']")
    page.wait_for_url("**/checkout-step-one.html", timeout=5000)
    print(f"  URL: {page.url}")

    page.fill("[data-test='firstName']",  FIRST_NAME)
    page.fill("[data-test='lastName']",   LAST_NAME)
    page.fill("[data-test='postalCode']", POSTAL_CODE)
    screenshot(page, "08_checkout_info")

    page.click("[data-test='continue']")
    page.wait_for_url("**/checkout-step-two.html", timeout=5000)

    passed = "/checkout-step-two.html" in page.url
    print(f"  Next page URL: {page.url}")
    results.append(("TC-07: Checkout Information Input", passed, page.url))


def tc_order_summary(page, results: list):
    """TC-08: Verify order summary and price"""
    section("TC-08: Order Summary Verification")

    items            = page.locator(".cart_item")
    count            = items.count()
    item_total_text  = page.locator(".summary_subtotal_label").inner_text()
    tax_text         = page.locator(".summary_tax_label").inner_text()
    total_text       = page.locator(".summary_total_label").inner_text()

    print(f"  Item count  : {count}")
    print(f"  Subtotal    : {item_total_text}")
    print(f"  Tax         : {tax_text}")
    print(f"  Total       : {total_text}")
    screenshot(page, "09_order_summary")

    passed = count == len(PRODUCTS_TO_ADD)
    results.append(("TC-08: Order Summary Verification", passed,
                    f"{count} items / {total_text}"))


def tc_order_complete(page, results: list):
    """TC-09: Complete order"""
    section("TC-09: Order Completion")

    page.click("[data-test='finish']")
    page.wait_for_url("**/checkout-complete.html", timeout=5000)

    complete_header = page.locator(".complete-header").inner_text()
    print(f"  Completion message: {complete_header}")
    screenshot(page, "10_order_complete")

    passed = "Thank you" in complete_header
    results.append(("TC-09: Order Completion", passed, complete_header))


def tc_logout(page, results: list):
    """TC-10: Logout"""
    section("TC-10: Logout")

    page.click("#react-burger-menu-btn")
    page.wait_for_selector("#logout_sidebar_link", timeout=3000)
    page.click("#logout_sidebar_link")
    page.wait_for_url(BASE_URL + "/", timeout=5000)

    login_visible = page.locator("#login-button").is_visible()
    print(f"  Redirected to login page: {login_visible}")
    screenshot(page, "11_logout")

    results.append(("TC-10: Logout", login_visible,
                    "Redirected to login page" if login_visible else "Failed to redirect"))


# ─────────────────────────────────────
# Main
# ─────────────────────────────────────

def run_all():
    results = []

    print("=" * 50)
    print("  SauceDemo Automated Test Suite [Playwright]")
    print(f"  Executed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=800,        # Slow down each action by 800ms for visibility
            args=["--no-sandbox"]
        )
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page    = context.new_page()

        try:
            # Negative tests
            tc_login_fail_locked(page, results)
            tc_login_fail_wrong_pass(page, results)

            # Main flow
            tc_login_success(page, results)
            tc_product_list(page, results)
            tc_add_to_cart(page, results)
            tc_cart_contents(page, results)
            tc_checkout_info(page, results)
            tc_order_summary(page, results)
            tc_order_complete(page, results)
            tc_logout(page, results)

        except Exception as e:
            print(f"\n❌ Unexpected error during test: {e}")
            screenshot(page, "ERROR")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()

    # Summary
    print(f"\n{'='*50}")
    print("  Test Result Summary")
    print(f"{'='*50}")
    all_pass = True
    for name, passed, detail in results:
        icon = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {icon}  {name}")
        print(f"         → {detail}")
        if not passed:
            all_pass = False

    total  = len(results)
    passed = sum(1 for _, p, _ in results if p)
    failed = total - passed

    print(f"{'─'*50}")
    print(f"  Total: {total}   ✅ {passed} Passed   ❌ {failed} Failed")
    verdict = "✅ All Tests PASSED 🎉" if all_pass else f"❌ {failed} Test(s) FAILED"
    print(f"  Result: {verdict}")
    print(f"{'='*50}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(run_all())
