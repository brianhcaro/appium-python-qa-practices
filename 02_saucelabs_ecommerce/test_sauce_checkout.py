"""Appium + Python end-to-end test: add a product to the cart (practice 02).

Drives the Sauce Labs mobile demo app (installed from a local APK) on the
physical Samsung device. Flow:

    open app -> click first product -> Add to cart -> assert badge = "1"
    -> success screenshot (evidence_sauce_add_to_cart.png)

Run:      python test_sauce_checkout.py
Requires: Appium Server running on http://127.0.0.1:4723, the Android device
          connected via adb, and the demo APK present (see APP_APK_PATH).

Locator strategy: preference order is accessibility-id, then unique
resource-id. All values below were verified from live page-source dumps on the
device (catalog, detail, and post-add screens), not guessed from docs.
"""

import json
import os

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ---------------------------------------------------------------------------
# CONFIGURATION — ADAPT THESE VALUES TO YOUR CASE
# ---------------------------------------------------------------------------

# Appium Server address. The default port for Appium 2/3 is 4723 (no /wd/hub).
APPIUM_SERVER_URL = "http://127.0.0.1:4723"

# --- Device ---
# Informational label; what really matters to Appium is the UDID below.
DEVICE_NAME = "SM-A336M"

# Local runtime configuration file, excluded from git (see .gitignore): it
# holds the physical device's UDID serial so the value never lands on GitHub.
CONFIG_FILE = "config.json"

# Android version as reported by the device: Settings > About phone, or
# `adb shell getprop ro.build.version.release`.
PLATFORM_VERSION = "16"

# --- App under test (installed from a local APK) ---
# Requested relative path to the downloaded Sauce Labs demo APK (see README
# of the practice). The path is relative to THIS script, resolved below.
APP_APK_PATH = "./apps/mqa-demo-app-android.apk"

# Fallback: the APK may live under "App/" with its original filename. The
# project rule is "never assume a single hardcoded value" — same idea applied
# to the APK location. Only one of these needs to exist.
APP_APK_FALLBACK = "./App/mda-2.3.0-27.apk"

# Screenshot evidence is saved next to this script.
EVIDENCE_SCREENSHOT = "evidence_sauce_add_to_cart.png"

# --- Product under test ---
# The first catalog tile, identified by its title on the detail screen.
PRODUCT_NAME = "Sauce Labs Backpack"
# Expected item count shown by the cart badge after one add.
EXPECTED_CART_COUNT = "1"

# --- Waits ---
# Hard ceiling for every explicit wait in this test (seconds). If the app is
# slower than this on a fresh device, bump it up here in one place.
WAIT_TIMEOUT_SECONDS = 20

# ---------------------------------------------------------------------------
# Locators — all verified from live UI dumps (catalog/detail/badge screens)
# ---------------------------------------------------------------------------
# Catalog screen:
#   - The product tile click surface is the IMAGE (id productIV), not the
#     title. The id repeats for every tile, so we take index 0 (document
#     order) for "the first product".
PRODUCT_IMAGE_ID = "com.saucelabs.mydemoapp.android:id/productIV"
#   - Header title "Products" acts as the "catalog loaded" smoke signal. Its
#     resource-id is productTV (shared with the detail title; safe because we
#     only use it while expecting the catalog).
CATALOG_TITLE_ID = "com.saucelabs.mydemoapp.android:id/productTV"
# Detail screen:
#   - Detail title text lives in the same resource-id productTV. Combined with
#     the product name it confirms we opened the RIGHT product.
DETAIL_TITLE_ID = "com.saucelabs.mydemoapp.android:id/productTV"
#   - "Add to cart" button: unique accessibility-id (content-desc) on a Button
#     with resource-id cartBt. Prefer the accessibility-id per project rules.
ADD_TO_CART_ACCESSIBILITY_ID = "Tap to add product to cart"
# Cart header (visible on every screen):
#   - The count badge is a TextView that only exists once at least one item is
#     in the cart. Unique resource-id: cartTV (inside cartCircleRL, cartRL).
CART_BADGE_ID = "com.saucelabs.mydemoapp.android:id/cartTV"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def resolve_apk_path(relative_path):
    """Return the absolute path of a path relative to this script.

    Appium needs an absolute path for the `app` capability: it resolves it
    against the server's working directory, not ours, so passing a bare
    relative path is unreliable. We anchor it to this file instead.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.abspath(os.path.join(script_dir, relative_path))
    return candidate if os.path.exists(candidate) else None


def find_available_apk():
    """Return the first APK path that exists, trying the requested one first."""
    for candidate in (APP_APK_PATH, APP_APK_FALLBACK):
        found = resolve_apk_path(candidate)
        if found is not None:
            return found
    raise FileNotFoundError(
        "APK not found. Expected it at one of these relative paths: "
        f"{APP_APK_PATH}, {APP_APK_FALLBACK} (next to this script). "
        "Download the Sauce Labs mobile demo app and place it there."
    )


def load_config():
    """Load runtime configuration from config.json (next to this script).

    Keeps device-specific secrets like the UDID serial out of the repository:
    the file is listed in .gitignore, so it is never committed to GitHub.
    """
    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), CONFIG_FILE
    )
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Missing local config file: {config_path}. Copy "
            "config.example.json to config.json and set your own UDID, "
            'e.g. {"udid": "R58M1234567"}. Configuration is intentionally '
            "not committed to git."
        )
    with open(config_path, "r", encoding="utf-8") as config_file:
        return json.load(config_file)


def build_android_options():
    """Build the UiAutomator2 capabilities for the physical Samsung device."""
    options = UiAutomator2Options()
    options.platform_name = "Android"          # OS we automate.
    options.automation_name = "UiAutomator2"   # Modern Android engine.
    options.device_name = DEVICE_NAME          # Label; UDID does the routing.
    # Point at the physical phone (from local config.json, not committed).
    options.udid = load_config()["udid"]
    options.platform_version = PLATFORM_VERSION
    # `app` instead of appPackage/appActivity: Appium installs the APK from a
    # local file, which also lets us run a freshly downloaded build without
    # knowing its package/id in advance.
    options.app = find_available_apk()
    # noReset=False: Appium clears the app's data when the session starts, so
    # every run begins with an EMPTY cart. This is required by the badge
    # assertion (assert badge == "1"): with noReset=True, items left in the
    # cart by previous runs would make the count nondeterministic (e.g. "2").
    # Clearing data does not uninstall the app, so no reinstall is triggered.
    options.no_reset = False
    # forceAppLaunch=True learned from practice 01: with noReset, Appium skips
    # launching when the app process is already alive. Forcing the launch makes
    # every run start deterministically on the app's main screen.
    options.force_app_launch = True
    # Give slow installs extra time between commands on this physical device.
    options.new_command_timeout = 120
    # Longer APK install window: the 90s default was exceeded on this device
    # while Google Play Protect dialogs were blocking sideloaded installs
    # (fixed by disabling the verifier for ADB installs on this test device).
    options.set_capability("androidInstallTimeout", 180000)
    return options


def create_driver():
    """Open the Appium session: Python <-> Appium Server <-> Android."""
    print("Building UiAutomator2 options...")
    options = build_android_options()
    print("Starting Appium session...")
    driver = webdriver.Remote(APPIUM_SERVER_URL, options=options)
    print(f"Session started. Session ID: {driver.session_id}")
    return driver


# ---------------------------------------------------------------------------
# Test case
# ---------------------------------------------------------------------------

def test_add_to_cart_flow(driver):
    """End-to-end flow: catalog -> first product -> Add to cart -> badge '1'.

    Explicit waits (WebDriverWait + expected conditions) are used instead of
    fixed sleeps, so the test is stable on slower devices and gives precise
    failures when a step never completes.
    """
    wait = WebDriverWait(driver, WAIT_TIMEOUT_SECONDS)

    # 1) Open the app (forceAppLaunch in options) and wait until the catalog
    #    header "Products" is visible. This is the reliable "we are home" check.
    wait.until(
        EC.visibility_of_element_located((AppiumBy.ID, CATALOG_TITLE_ID))
    )
    print("Step 1 OK: catalog loaded.")

    # 2) Click the FIRST product tile. The image is the clickable surface and
    #    the resource-id repeats per tile, so index 0 selects the first one.
    first_product_image = wait.until(
        EC.presence_of_all_elements_located((AppiumBy.ID, PRODUCT_IMAGE_ID))
    )[0]
    first_product_image.click()
    print("Step 2 OK: first product image clicked.")

    # 3) Detail screen: confirm we opened the right product, then wait for the
    #    Add to cart button (unique accessibility-id) to be tappable.
    wait.until(
        EC.visibility_of_element_located(
            (AppiumBy.ANDROID_UIAUTOMATOR,
             f'new UiSelector().resourceId("{DETAIL_TITLE_ID}")'
             f'.text("{PRODUCT_NAME}")')
        )
    )
    add_to_cart = wait.until(
        EC.element_to_be_clickable(
            (AppiumBy.ACCESSIBILITY_ID, ADD_TO_CART_ACCESSIBILITY_ID)
        )
    )
    add_to_cart.click()
    print("Step 3 OK: Add to cart clicked.")

    # 4) Assert the cart badge shows "1". The badge TextView (id cartTV) only
    #    exists once the cart has items; its text is the item count.
    badge = wait.until(
        EC.visibility_of_element_located((AppiumBy.ID, CART_BADGE_ID))
    )
    badge_text = badge.text.strip()
    assert badge_text == EXPECTED_CART_COUNT, (
        f"Expected cart badge '{EXPECTED_CART_COUNT}', got '{badge_text}'."
    )
    print(f"Step 4 OK: cart badge shows '{badge_text}'.")

    # 5) Success screenshot. save_screenshot returns True when written.
    evidence_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), EVIDENCE_SCREENSHOT
    )
    saved = driver.save_screenshot(evidence_path)
    print(f"Screenshot saved ({saved}): {evidence_path}")
    if not saved:
        raise RuntimeError("Screenshot was not saved; check device/session state.")

    print("Test completed successfully.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    driver = None  # So the finally block can check it if setup failed.
    try:
        driver = create_driver()
        test_add_to_cart_flow(driver)
    except Exception as error:
        # Re-raise after cleanup: a failing test must produce a non-zero exit.
        print(f"Test failed: {type(error).__name__}: {error}")
        raise
    finally:
        # Always close the session: Appium resources are freed even on failure.
        if driver is not None:
            driver.quit()
            print("Appium session closed.")