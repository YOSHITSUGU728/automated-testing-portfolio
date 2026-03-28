"""
Authentication Flow API Test
Target: Restful Booker (https://restful-booker.herokuapp.com)
Framework: Playwright (Python) - APIRequestContext
Author: YOSHITSUGU728

Test Cases:
    TC01 - Successful login -> Token acquisition
    TC02 - Failed login (wrong password) -> Error verification
    TC03 - Create booking with valid token (POST)
    TC04 - Update booking with valid token (PUT)
    TC05 - Delete booking with valid token (DELETE)
    TC06 - Access protected endpoint without token -> 403 Forbidden
"""

import pytest
from playwright.sync_api import Playwright, APIRequestContext

BASE_URL = "https://restful-booker.herokuapp.com"
USERNAME = "admin"
PASSWORD = "password123"


# ─────────────────────────────────────────────
# Fixture: APIRequestContext
# ─────────────────────────────────────────────
@pytest.fixture(scope="session")
def api_request_context(playwright: Playwright) -> APIRequestContext:
    context = playwright.request.new_context(base_url=BASE_URL)
    yield context
    context.dispose()


# ─────────────────────────────────────────────
# Fixture: Auth token (shared across session)
# ─────────────────────────────────────────────
@pytest.fixture(scope="session")
def auth_token(api_request_context: APIRequestContext) -> str:
    response = api_request_context.post(
        "/auth",
        data={"username": USERNAME, "password": PASSWORD},
    )
    assert response.status == 200, f"Failed to retrieve token: {response.status}"
    token = response.json().get("token")
    assert token, "Token not found in response"
    return token


# ─────────────────────────────────────────────
# Fixture: Booking ID (created in TC03, used in TC04/TC05)
# ─────────────────────────────────────────────
@pytest.fixture(scope="session")
def booking_id(api_request_context: APIRequestContext, auth_token: str) -> int:
    response = api_request_context.post(
        "/booking",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        data="""{
            "firstname": "Taro",
            "lastname": "Yamada",
            "totalprice": 12000,
            "depositpaid": true,
            "bookingdates": {
                "checkin": "2025-01-01",
                "checkout": "2025-01-05"
            },
            "additionalneeds": "Breakfast"
        }""",
    )
    assert response.status == 200
    booking_id = response.json().get("bookingid")
    assert booking_id, "Booking ID not found in response"
    return booking_id


# ─────────────────────────────────────────────
# TC01: Successful login -> Token acquisition
# ─────────────────────────────────────────────
def test_tc01_login_success(api_request_context: APIRequestContext):
    """TC01: Verify that a valid token is returned with correct credentials"""
    response = api_request_context.post(
        "/auth",
        data={"username": USERNAME, "password": PASSWORD},
    )

    assert response.status == 200, f"Expected status 200, got: {response.status}"

    body = response.json()
    assert "token" in body, "Token not found in response body"
    assert len(body["token"]) > 0, "Token is empty"

    print(f"\n✅ TC01 PASS | Token acquired: {body['token']}")


# ─────────────────────────────────────────────
# TC02: Failed login (wrong password)
# ─────────────────────────────────────────────
def test_tc02_login_failure(api_request_context: APIRequestContext):
    """TC02: Verify that no token is issued with incorrect credentials"""
    response = api_request_context.post(
        "/auth",
        data={"username": USERNAME, "password": "wrongpassword"},
    )

    assert response.status == 200, f"Expected status 200, got: {response.status}"

    body = response.json()
    assert "token" not in body, "Token should not be returned with wrong password"
    assert body.get("reason") == "Bad credentials", (
        f"Unexpected error message: {body.get('reason')}"
    )

    print(f"\n✅ TC02 PASS | Login failure correctly detected: {body}")


# ─────────────────────────────────────────────
# TC03: Create booking with valid token (POST)
# ─────────────────────────────────────────────
def test_tc03_create_booking_with_token(
    api_request_context: APIRequestContext, auth_token: str, booking_id: int
):
    """TC03: Verify that a booking can be created with a valid token"""
    assert booking_id > 0, "Booking ID is invalid"

    print(f"\n✅ TC03 PASS | Booking created successfully (BookingID: {booking_id})")


# ─────────────────────────────────────────────
# TC04: Update booking with valid token (PUT)
# ─────────────────────────────────────────────
def test_tc04_update_booking_with_token(
    api_request_context: APIRequestContext, auth_token: str, booking_id: int
):
    """TC04: Verify that a booking can be updated with a valid token"""
    response = api_request_context.put(
        f"/booking/{booking_id}",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Cookie": f"token={auth_token}",
        },
        data="""{
            "firstname": "Hanako",
            "lastname": "Yamada",
            "totalprice": 15000,
            "depositpaid": false,
            "bookingdates": {
                "checkin": "2025-02-01",
                "checkout": "2025-02-07"
            },
            "additionalneeds": "Dinner"
        }""",
    )

    assert response.status == 200, f"Booking update failed: {response.status}"

    body = response.json()
    assert body.get("firstname") == "Hanako", "firstname was not updated"
    assert body.get("totalprice") == 15000, "totalprice was not updated"

    print(f"\n✅ TC04 PASS | Booking updated successfully: {body}")


# ─────────────────────────────────────────────
# TC05: Delete booking with valid token (DELETE)
# ─────────────────────────────────────────────
def test_tc05_delete_booking_with_token(
    api_request_context: APIRequestContext, auth_token: str, booking_id: int
):
    """TC05: Verify that a booking can be deleted with a valid token"""
    response = api_request_context.delete(
        f"/booking/{booking_id}",
        headers={"Cookie": f"token={auth_token}"},
    )

    assert response.status == 201, f"Booking deletion failed: {response.status}"

    print(f"\n✅ TC05 PASS | Booking deleted successfully (BookingID: {booking_id})")


# ─────────────────────────────────────────────
# TC06: Access protected endpoint without token -> 403 Forbidden
# ─────────────────────────────────────────────
def test_tc06_delete_booking_without_token(
    api_request_context: APIRequestContext, booking_id: int
):
    """TC06: Verify that a delete request is rejected without a valid token"""
    response = api_request_context.delete(
        f"/booking/{booking_id}",
        headers={},  # No token
    )

    assert response.status == 403, (
        f"Expected 403 Forbidden, got: {response.status}"
    )

    print(f"\n✅ TC06 PASS | Unauthorized access correctly rejected: status={response.status}")
