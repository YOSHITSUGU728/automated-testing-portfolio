"""
=============================================================
Form Validation Test (Selenium)
Target: https://the-internet.herokuapp.com/login
Valid credentials: tomsmith / SuperSecretPassword!

Usage:
  pip install selenium webdriver-manager

  python form_validation_test.py             # Show browser (default)
  python form_validation_test.py --headless  # Run headless (no browser)
=============================================================
"""

import argparse
import csv
import json
import os
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

# =====================================================================
# Test Cases (35 cases)
# =====================================================================
TEST_CASES = [
    # ── Full-width characters ─────────────────────────────────────────
    {"id": "Z-01", "category": "Full-width", "name": "Full-width alpha username",
     "username": "ａｄｍｉｎ", "password": "admin", "expected_error": True,
     "note": "Full-width letters are outside ASCII and should cause an auth error"},
    {"id": "Z-02", "category": "Full-width", "name": "Full-width numeric password",
     "username": "admin", "password": "１２３４５６", "expected_error": True,
     "note": "Full-width numbers are outside ASCII and should cause an auth error"},
    {"id": "Z-03", "category": "Full-width", "name": "Full-width space in username",
     "username": "　admin　", "password": "admin", "expected_error": True,
     "note": "Full-width spaces cannot be trimmed and should cause an auth error"},
    {"id": "Z-04", "category": "Full-width", "name": "Japanese username",
     "username": "テスト管理者", "password": "admin", "expected_error": True,
     "note": "Japanese characters should cause an auth error"},
    {"id": "Z-05", "category": "Full-width", "name": "Japanese password",
     "username": "admin", "password": "パスワード1234", "expected_error": True,
     "note": "Japanese password should cause an auth error"},
    {"id": "Z-06", "category": "Full-width", "name": "Hiragana only",
     "username": "あいうえお", "password": "かきくけこ", "expected_error": True,
     "note": "Hiragana characters should cause an auth error"},
    {"id": "Z-07", "category": "Full-width", "name": "Katakana only",
     "username": "アドミン", "password": "パスワード", "expected_error": True,
     "note": "Katakana characters should cause an auth error"},
    {"id": "Z-08", "category": "Full-width", "name": "Full-width symbols in username",
     "username": "ａｄｍｉｎ！", "password": "ｐａｓｓ", "expected_error": True,
     "note": "Full-width symbols should cause an auth error"},
    # ── Half-width characters ─────────────────────────────────────────
    {"id": "H-01", "category": "Half-width", "name": "Valid login (correct credentials)",
     "username": "tomsmith", "password": "SuperSecretPassword!", "expected_error": True,  # ★ Demo: intentionally wrong expected value to trigger FAIL + screenshot
     "note": "Correct credentials should succeed and redirect to /secure"},
    {"id": "H-02", "category": "Half-width", "name": "Uppercase username",
     "username": "TOMSMITH", "password": "SuperSecretPassword!", "expected_error": True,
     "note": "Username is case-sensitive and should cause an auth error"},
    {"id": "H-03", "category": "Half-width", "name": "Lowercase password",
     "username": "tomsmith", "password": "supersecretpassword!", "expected_error": True,
     "note": "Password is case-sensitive and should cause an auth error"},
    {"id": "H-04", "category": "Half-width", "name": "Numeric-only username",
     "username": "12345", "password": "admin", "expected_error": True,
     "note": "Numeric-only username should cause an auth error"},
    {"id": "H-05", "category": "Half-width", "name": "Numeric-only password",
     "username": "admin", "password": "123456", "expected_error": True,
     "note": "Numeric-only password should cause an auth error"},
    {"id": "H-06", "category": "Half-width", "name": "Space in username",
     "username": "tom smith", "password": "SuperSecretPassword!", "expected_error": True,
     "note": "Username with space should cause an auth error"},
    {"id": "H-07", "category": "Half-width", "name": "Email format username",
     "username": "tom@example.com", "password": "SuperSecretPassword!", "expected_error": True,
     "note": "Email-format username should cause an auth error"},
    # ── Length / boundary ─────────────────────────────────────────────
    {"id": "L-01", "category": "Length", "name": "Empty username",
     "username": "", "password": "admin", "expected_error": True,
     "note": "Empty username should cause an error"},
    {"id": "L-02", "category": "Length", "name": "Empty password",
     "username": "admin", "password": "", "expected_error": True,
     "note": "Empty password should cause an error"},
    {"id": "L-03", "category": "Length", "name": "Both fields empty",
     "username": "", "password": "", "expected_error": True,
     "note": "Both empty fields should cause an error"},
    {"id": "L-04", "category": "Length", "name": "1-char username",
     "username": "a", "password": "admin", "expected_error": True,
     "note": "Single-character username should cause an auth error"},
    {"id": "L-05", "category": "Length", "name": "1-char password",
     "username": "admin", "password": "a", "expected_error": True,
     "note": "Single-character password should cause an auth error"},
    {"id": "L-06", "category": "Length", "name": "50-char username",
     "username": "a" * 50, "password": "admin", "expected_error": True,
     "note": "50-character username should cause an auth error"},
    {"id": "L-07", "category": "Length", "name": "255-char username",
     "username": "a" * 255, "password": "admin", "expected_error": True,
     "note": "255-character username should cause an auth error"},
    {"id": "L-08", "category": "Length", "name": "255-char password",
     "username": "admin", "password": "a" * 255, "expected_error": True,
     "note": "255-character password should cause an auth error"},
    {"id": "L-09", "category": "Length", "name": "2-char username (boundary lower)",
     "username": "ab", "password": "admin", "expected_error": True,
     "note": "Boundary value test: 2 characters"},
    {"id": "L-10", "category": "Length", "name": "3-char username (boundary)",
     "username": "abc", "password": "admin", "expected_error": True,
     "note": "Boundary value test: 3 characters"},
    # ── Special characters ────────────────────────────────────────────
    {"id": "S-01", "category": "Special chars", "name": "SQL injection",
     "username": "' OR '1'='1", "password": "' OR '1'='1", "expected_error": True,
     "note": "SQL injection attempt should fail (no bypass allowed)"},
    {"id": "S-02", "category": "Special chars", "name": "XSS attempt",
     "username": "<script>alert('xss')</script>", "password": "admin", "expected_error": True,
     "note": "XSS string should be sanitized and cause an auth error"},
    {"id": "S-03", "category": "Special chars", "name": "Symbols-only username",
     "username": "!@#$%^&*()", "password": "admin", "expected_error": True,
     "note": "Symbols-only username should cause an auth error"},
    {"id": "S-04", "category": "Special chars", "name": "Backslash in username",
     "username": "admin\\test", "password": "admin", "expected_error": True,
     "note": "Backslash in username should cause an auth error"},
    {"id": "S-05", "category": "Special chars", "name": "Newline in username",
     "username": "admin\ntest", "password": "admin", "expected_error": True,
     "note": "Newline character in username should cause an auth error"},
    {"id": "S-06", "category": "Special chars", "name": "Tab in username",
     "username": "admin\ttest", "password": "admin", "expected_error": True,
     "note": "Tab character in username should cause an auth error"},
    {"id": "S-07", "category": "Special chars", "name": "Hyphen and underscore",
     "username": "tom-smith_01", "password": "admin", "expected_error": True,
     "note": "Hyphen/underscore username should cause an auth error"},
    {"id": "S-08", "category": "Special chars", "name": "Dot in username",
     "username": "tom.smith", "password": "admin", "expected_error": True,
     "note": "Dot in username should cause an auth error"},
    {"id": "S-09", "category": "Special chars", "name": "Emoji in username",
     "username": "admin😀", "password": "admin", "expected_error": True,
     "note": "Emoji in username should cause an auth error"},
    {"id": "S-10", "category": "Special chars", "name": "URL-encoded characters",
     "username": "admin%20test", "password": "admin", "expected_error": True,
     "note": "URL-encoded string should not be decoded and should cause an auth error"},
]

TARGET_URL  = "https://the-internet.herokuapp.com/login"
SUCCESS_URL = "https://the-internet.herokuapp.com/secure"


# =====================================================================
# Result dataclass
# =====================================================================
@dataclass
class TestResult:
    id: str
    category: str
    name: str
    username: str
    password: str
    expected_error: bool
    note: str
    status: str                  = "PENDING"
    actual_error: Optional[bool] = None
    error_message: str           = ""
    duration_ms: int             = 0
    screenshot: str              = ""


# =====================================================================
# Verdict helper
# =====================================================================
def _judge(actual_url: str, flash_class: str, flash_text: str) -> tuple:
    if SUCCESS_URL in actual_url:
        return False, flash_text.strip()
    cls = flash_class.lower()
    if "error" in cls or "alert" in cls:
        return True, flash_text.strip()
    if "success" in cls or "notice" in cls:
        return False, flash_text.strip()
    if flash_text.strip():
        return True, flash_text.strip()
    return False, ""


# =====================================================================
# Selenium test runner
# =====================================================================
def run_all(headless: bool = False) -> list[TestResult]:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException
    from webdriver_manager.chrome import ChromeDriverManager

    def build_driver():
        opts = Options()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1280,800")
        opts.add_argument("--log-level=3")
        opts.add_argument("--disable-features=PasswordLeakDetection,PasswordManager,SafeBrowsingEnhancedProtection")
        opts.add_argument("--disable-save-password-bubble")
        opts.add_argument("--disable-password-generation")
        opts.add_argument("--no-default-browser-check")
        opts.add_experimental_option("excludeSwitches", ["enable-logging"])
        opts.add_experimental_option("prefs", {
            "credentials_enable_service": False,
            "credentials_enable_autosignin": False,
            "profile.password_manager_enabled": False,
            "profile.password_manager_leak_detection": False,
            "safebrowsing.enabled": False,
            "safebrowsing.enhanced": False,
        })
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=opts
        )

    def run_one(driver, tc) -> TestResult:
        r = TestResult(
            **{k: tc[k] for k in
               ("id", "category", "name", "username", "password", "expected_error", "note")}
        )
        start = time.time()
        try:
            driver.get(TARGET_URL)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )

            u_elem = driver.find_element(By.ID, "username")
            p_elem = driver.find_element(By.ID, "password")

            # Set values via JS (safe for newlines, tabs, special chars)
            driver.execute_script("arguments[0].value = arguments[1];", u_elem, tc["username"])
            driver.execute_script("arguments[0].value = arguments[1];", p_elem, tc["password"])

            # Disable HTML5 validation so empty fields reach the server
            driver.execute_script(
                "document.querySelector('form').setAttribute('novalidate','true');"
            )
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            # Wait for URL change or flash message (max 5s)
            try:
                WebDriverWait(driver, 5).until(
                    lambda d: SUCCESS_URL in d.current_url
                    or len(d.find_elements(By.ID, "flash")) > 0
                )
            except TimeoutException:
                pass

            actual_url  = driver.current_url
            flash_class = ""
            flash_text  = ""
            try:
                el = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "flash"))
                )
                flash_class = el.get_attribute("class") or ""
                flash_text  = el.text.strip()
            except Exception:
                pass

            r.actual_error, r.error_message = _judge(actual_url, flash_class, flash_text)

            # Log out after successful login
            if not r.actual_error:
                try:
                    driver.find_element(
                        By.CSS_SELECTOR, "a.button[href='/logout']"
                    ).click()
                    time.sleep(1)
                except Exception:
                    pass

            r.status = "PASS" if r.expected_error == r.actual_error else "FAIL"

            # Save screenshot only on FAIL
            if r.status == "FAIL":
                os.makedirs("screenshots", exist_ok=True)
                ss = f"screenshots/{tc['id']}_FAIL.png"
                driver.save_screenshot(ss)
                r.screenshot = ss

        except TimeoutException:
            r.status        = "ERROR"
            r.error_message = "TimeoutException: page load timed out"
        except Exception as e:
            r.status        = "ERROR"
            r.error_message = f"{type(e).__name__}: {str(e)[:80]}"

        r.duration_ms = int((time.time() - start) * 1000)
        return r

    mode = "headless" if headless else "headed"
    print()
    print("=" * 62)
    print(f"  Selenium Form Validation Test ({mode})")
    print(f"  Target : {TARGET_URL}")
    print(f"  Cases  : {len(TEST_CASES)}")
    print(f"  Start  : {datetime.now():%Y-%m-%d %H:%M:%S}")
    print("=" * 62)

    driver  = build_driver()
    results = []
    try:
        for i, tc in enumerate(TEST_CASES, 1):
            print(f"  ({i:02d}/{len(TEST_CASES)}) {tc['name']} ... ", end="", flush=True)
            r = run_one(driver, tc)
            results.append(r)
            icon = {"PASS": "✅", "FAIL": "❌", "ERROR": "⚠️"}.get(r.status, "?")
            print(f"{icon} {r.status} ({r.duration_ms}ms)")
            if r.status != "PASS":
                print(f"       → expected_error:{r.expected_error} / actual_error:{r.actual_error}")
                if r.error_message:
                    print(f"       → {r.error_message[:70]}")
                if r.screenshot:
                    print(f"       📸 {r.screenshot}")
    finally:
        driver.quit()

    return results


# =====================================================================
# Report output
# =====================================================================
def save_csv(results: list[TestResult], path: str):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow([
            "ID", "Category", "Test Case",
            "Username (first 40)", "Password (first 40)",
            "Expected Error", "Actual Error",
            "Status", "Message", "Duration(ms)", "Screenshot", "Notes"
        ])
        for r in results:
            w.writerow([
                r.id, r.category, r.name,
                r.username[:40], r.password[:40],
                r.expected_error, r.actual_error,
                r.status, r.error_message,
                r.duration_ms, r.screenshot, r.note
            ])


def save_json(results: list[TestResult], path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in results], f, ensure_ascii=False, indent=2)


def print_summary(results: list[TestResult]):
    total  = len(results)
    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")
    errors = sum(1 for r in results if r.status == "ERROR")

    print()
    print("─" * 62)
    print("  Test Summary")
    print("─" * 62)
    print(f"  Total  : {total}")
    print(f"  ✅ PASS  : {passed}")
    print(f"  ❌ FAIL  : {failed}")
    print(f"  ⚠️  ERROR : {errors}")
    print(f"  Rate   : {passed / total * 100:.1f}%")

    if failed or errors:
        print()
        print("  ▼ Issues")
        for r in results:
            if r.status in ("FAIL", "ERROR"):
                print(f"    [{r.id}] {r.name}")
                if r.error_message:
                    print(f"           {r.error_message[:60]}")
    print("─" * 62)


# =====================================================================
# Entry point
# =====================================================================
def main():
    parser = argparse.ArgumentParser(description="Selenium Form Validation Test")
    parser.add_argument("--headless", action="store_true",
                        help="Run in headless mode (no browser window)")
    args = parser.parse_args()

    results = run_all(headless=args.headless)
    print_summary(results)

    ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path  = f"report_{ts}.csv"
    json_path = f"report_{ts}.json"
    save_csv(results, csv_path)
    save_json(results, json_path)

    print()
    print(f"  📄 {csv_path}")
    print(f"  📄 {json_path}")
    print(f"  Done: {datetime.now():%Y-%m-%d %H:%M:%S}")
    print()


if __name__ == "__main__":
    main()
