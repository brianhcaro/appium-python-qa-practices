"""
First mobile automation script with Appium + Python (Android).

Before running it:
1. Install the libraries (in the Cursor terminal):
   pip install Appium-Python-Client
2. Confirm the Appium Server is running (normally at http://127.0.0.1:4723).
3. Connect your phone by USB (with USB debugging) or start an emulator.
4. Run: adb devices
   You must see at least one device with state "device".
5. Create the local config file: copy config.example.json to config.json
   and put your own serial from "adb devices" in the "udid" field.
6. Run this file: python test_mi_app.py
"""

# Imports "json" to read the local config file (device UDID).
import json

# Imports the "time" module so we can wait a few seconds if needed.
import time

# Imports "os" to build file paths (for example, if you use a local APK).
import os

# Imports WebDriverWait: smart wait until an element exists or is clickable.
from selenium.webdriver.support.ui import WebDriverWait

# Imports expected_conditions: ready-made conditions (visible, clickable, etc.).
from selenium.webdriver.support import expected_conditions as EC

# Imports AppiumBy: indicates HOW to search for elements (id, xpath, accessibility id, etc.).
from appium.webdriver.common.appiumby import AppiumBy

# Imports Appium's webdriver: it is the "remote control" that talks to the phone.
from appium import webdriver

# Imports UiAutomator2Options: the recommended way (Appium 2 / W3C) to send capabilities.
from appium.options.android import UiAutomator2Options


# =============================================================================
# CONFIGURATION — ADAPT THESE VALUES TO YOUR CASE
# =============================================================================

# Appium server URL. In Appium 2 you do NOT use "/wd/hub" at the end.
APPIUM_SERVER_URL = "http://127.0.0.1:4723"

# Logical device name. On Android it is informational; what matters is the UDID.
# Emulator: you can leave "Android Emulator".
# Physical phone: you can put "My Pixel" or whatever model you like.
DEVICE_NAME = "SM-A336M"

# Local runtime configuration file, excluded from git (see the repository's
# .gitignore): it holds the physical device's UDID serial, so the value never
# lands on GitHub. Copy config.example.json to config.json and set your own
# serial from "adb devices" (or leave it null to let Appium pick the only
# connected device).
CONFIG_FILE = "config.json"

# Android version (optional but useful). Example: "14", "13", "12".
# You see it in Settings > About phone, or with: adb shell getprop ro.build.version.release
PLATFORM_VERSION = "16"  # Your Samsung SM-A336M reported Android 16

# ----- Option A: open an app that is ALREADY INSTALLED (recommended to start) -----
# appPackage: the application's ID. On Android it looks like a dotted name.
# How to get it: adb shell dumpsys window | findstr mCurrentFocus
APP_PACKAGE = "com.android.settings"

# appActivity: the app's launch screen.
# It also appears in the command above, after the package, separated by "/".
APP_ACTIVITY = ".Settings"

# ----- Option B: install and open an APK from your PC -----
# If you want to use an .apk file, put the full path and leave APP_PACKAGE/APP_ACTIVITY
# or fill them in as well. If you do not use an APK, leave this variable as None.
# Windows example: r"C:\Users\zero_\Downloads\mi_app.apk"
APP_APK_PATH = None


def load_config():
    """Loads runtime configuration from config.json (next to this script).

    Keeps device-specific secrets like the UDID serial out of the repository:
    the file is listed in .gitignore, so it is never committed to GitHub.
    Copy config.example.json to config.json and set your own values.
    """
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_FILE)
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Missing local config file: {config_path}. Copy config.example.json "
            'to config.json and set your own UDID, e.g. {"udid": "R58M1234567"}. '
            "Configuration is intentionally not committed to git."
        )
    with open(config_path, "r", encoding="utf-8") as config_file:
        return json.load(config_file)


def build_android_options():
    """Builds the Desired Capabilities / Options for Android (physical device or emulator)."""

    # Creates the Android options object with the UiAutomator2 engine (the current standard).
    options = UiAutomator2Options()

    # platformName: operating system. For this script it is always Android.
    options.platform_name = "Android"

    # automationName: automation engine. UiAutomator2 is the one for modern Android.
    options.automation_name = "UiAutomator2"

    # deviceName: device label. Appium 2 requires it, but the actual device is chosen by UDID.
    options.device_name = DEVICE_NAME

    # Device serial comes from the local config.json (gitignored), so the
    # physical device ID never lands on GitHub. If the config value is null,
    # Appium picks the only connected device (useful when there is only one).
    udid = load_config().get("udid")
    if udid:
        # udid: the exact serial from "adb devices". Essential if you have more than one device.
        options.udid = udid

    # If you defined the Android version, we add it (it helps Appium validate the environment).
    if PLATFORM_VERSION:
        # platformVersion: "13", "14", etc. It must match the chosen device.
        options.platform_version = PLATFORM_VERSION

    # noReset=True: does not wipe the app's data on start. Faster and less invasive.
    options.no_reset = True

    # forceAppLaunch=True: forces Appium to launch the app even if its process is
    # already alive in the background. It is ESSENTIAL on this phone! Settings is
    # a system app (its process almost always exists), so with noReset=True
    # Appium skipped the launch: the test failed because the app NEVER
    # opened (the problem was not the locator, we simply were not in Settings).
    # Verified in the driver source code: if (noReset && !forceAppLaunch
    # && processExists(appPackage)) -> it does not launch the app.
    options.set_capability("forceAppLaunch", True)

    # newCommandTimeout: seconds Appium waits between commands before ending the session.
    options.new_command_timeout = 120

    # If there is an APK path, Appium installs (if needed) and opens that app.
    if APP_APK_PATH:
        # os.path.abspath converts the path into an absolute path that Appium understands better.
        options.app = os.path.abspath(APP_APK_PATH)
    else:
        # appPackage: which application to open (it must be installed on the device).
        options.app_package = APP_PACKAGE

        # appActivity: which screen to open inside that application.
        options.app_activity = APP_ACTIVITY

    # Returns the object ready to create the driver.
    return options


def create_driver():
    """Opens the Appium session: connects Python <-> Appium Server <-> Android."""

    # Calls the function that builds the capabilities/options.
    options = build_android_options()

    # webdriver.Remote creates the "driver": the object you will use for clicks, writes, asserts.
    driver = webdriver.Remote(command_executor=APPIUM_SERVER_URL, options=options)

    # implicit wait: if an element is not there, it waits up to 10 seconds before failing.
    driver.implicitly_wait(10)

    # Returns the driver already connected to the device.
    return driver


def wait_for_element(driver, locator, timeout=15):
    """Waits until an element is clickable. Best practice vs a fixed time.sleep."""

    # WebDriverWait checks the condition every so often until "timeout" seconds.
    wait = WebDriverWait(driver, timeout)

    # EC.element_to_be_clickable waits for the element to exist and be tappable.
    element = wait.until(EC.element_to_be_clickable(locator))

    # Returns the element ready to use (.click(), .send_keys(), .text, etc.).
    return element


def test_open_settings_and_search():
    """Example test case: opens Settings and uses the search box if it exists."""

    # driver starts as None in case the connection fails; that way the finally can check it.
    driver = None

    # try/except/finally: if anything fails, we still close the session (good practice).
    try:
        # Creates the session and launches the configured app (Settings by default).
        driver = create_driver()

        # Prints the session id to confirm Appium accepted the connection.
        print(f"Session started. Session ID: {driver.session_id}")

        # Prints the screen size (useful for understanding the device).
        print(f"Screen size: {driver.get_window_size()}")

        # Clean starting point: every run must begin on the Settings homepage.
        # Finding verified with adb on this Samsung: the search screen runs in
        # ANOTHER package (com.android.settings.intelligence/.search.SearchActivity). If a
        # previous run left it open, Settings' "am start" does NOT replace it (focus
        # stayed on SearchActivity) and the test failed at the button because the homepage
        # was never visible.

        # Force-stops the leftover search screen: it belongs to a different package than
        # the app under test and that is why it "resists" the relaunch of Settings.
        # If it was not open, this is a no-op (nothing happens).
        driver.terminate_app("com.android.settings.intelligence")

        # Brings Settings to the foreground using the APP_PACKAGE variable from the
        # CONFIGURATION section (equivalent to "am start" of its main activity).
        # That way, every run starts on the Settings homepage and the button is visible.
        driver.activate_app(APP_PACKAGE)

        # Locates the Settings search button with several chained locators
        # (a "fallback" strategy), same rationale as the search field.
        # Why? Verified with page source on this Samsung (One UI, SM-A336M): the
        # button is a Button with content-desc="Buscar en Configuración" and WITHOUT
        # its own resource-id. "Search"/"Buscar" alone do NOT match (ACCESSIBILITY_ID
        # compares EXACTLY), which is why the test failed here with TimeoutException.
        try:
            # 1) REAL locator verified on this device (page source).
            search_button = wait_for_element(
                driver,
                (AppiumBy.ACCESSIBILITY_ID, "Buscar en Configuración"),
                timeout=8,
            )
            print("Button located with: ACCESSIBILITY_ID 'Buscar en Configuración'")
        except Exception:
            # 2) One UI English variant: reasonable but NOT verified.
            try:
                search_button = wait_for_element(
                    driver,
                    (AppiumBy.ACCESSIBILITY_ID, "Search in Settings"),
                    timeout=6,
                )
                print("Button located with: ACCESSIBILITY_ID 'Search in Settings'")
            except Exception:
                # 3) Generic Android variant in Spanish (the one that was already there).
                try:
                    search_button = wait_for_element(
                        driver, (AppiumBy.ACCESSIBILITY_ID, "Buscar"), timeout=6
                    )
                    print("Button located with: ACCESSIBILITY_ID 'Buscar'")
                except Exception:
                    # 4) Generic Android variant in English (the one that was already there).
                    try:
                        search_button = wait_for_element(
                            driver, (AppiumBy.ACCESSIBILITY_ID, "Search"), timeout=6
                        )
                        print("Button located with: ACCESSIBILITY_ID 'Search'")
                    except Exception:
                        # 5) Last resort: an XPath that is "immune to text variations".
                        #    contains() accepts any content-desc that contains
                        #    "uscar" ("Buscar en Configuración", "Buscar", ...),
                        #    without depending on the full text or the exact translation.
                        try:
                            search_button = wait_for_element(
                                driver,
                                (
                                    AppiumBy.XPATH,
                                    '//android.widget.Button[contains(@content-desc, "uscar")]',
                                ),
                                timeout=6,
                            )
                            print(
                                "Button located with: XPath //android.widget.Button"
                                "[contains(@content-desc, 'uscar')]"
                            )
                        except Exception:
                            # If ALL of them fail, we print a clear message and let the
                            # error bubble up to the general except below (we do not swallow it).
                            print(
                                "Search button not found with any "
                                "of the tried locators (ACCESSIBILITY_ID 'Buscar en "
                                "Configuración'/'Search in Settings'/'Buscar'/'Search', "
                                "XPath Button[contains(@content-desc, 'uscar')])."
                            )
                            raise

        # Taps the search button.
        search_button.click()

        # Locates the search field with several chained locators
        # (a "fallback" strategy), same rationale as the button.
        # Why? Verified with page source on this Samsung after clicking the button:
        # One UI opens com.android.settings.intelligence/.search.SearchActivity and the
        # field is an AutoCompleteTextView (NOT an EditText), with resource-id
        # "...:id/search_src_text" and NO content-desc. That is why the previous chain
        # failed on all 4 attempts. We try several in order, each with a short timeout:
        # if one does not appear, we catch the exception and move to the next.
        try:
            # 1) REAL locator verified on this device: the exact class that
            #    One UI uses. It does not depend on the language or the app package.
            search_field = wait_for_element(
                driver,
                (AppiumBy.CLASS_NAME, "android.widget.AutoCompleteTextView"),
                timeout=8,
            )
            print("Field located with: CLASS_NAME 'android.widget.AutoCompleteTextView'")
        except Exception:
            # 2) XPath with a union ("|"): covers vanilla Android (EditText) and One UI
            #    (AutoCompleteTextView) in a single attempt.
            try:
                search_field = wait_for_element(
                    driver,
                    (
                        AppiumBy.XPATH,
                        "//android.widget.EditText | //android.widget.AutoCompleteTextView",
                    ),
                    timeout=6,
                )
                print("Field located with: XPath EditText | AutoCompleteTextView")
            except Exception:
                # 3) resource-id verified in the page source, but TIED to the package/
                #    One UI version: if Samsung changes that id (or the search app
                #    changes package), this attempt stops working.
                try:
                    search_field = wait_for_element(
                        driver,
                        (
                            AppiumBy.ID,
                            "com.android.settings.intelligence:id/search_src_text",
                        ),
                        timeout=6,
                    )
                    print("Field located with: ID search_src_text")
                except Exception:
                    # 4) Generic Android variant in Spanish (in case on some
                    #    model the field does expose content-desc).
                    try:
                        search_field = wait_for_element(
                            driver, (AppiumBy.ACCESSIBILITY_ID, "Buscar"), timeout=6
                        )
                        print("Field located with: ACCESSIBILITY_ID 'Buscar'")
                    except Exception:
                        # 5) Generic Android variant in English.
                        try:
                            search_field = wait_for_element(
                                driver, (AppiumBy.ACCESSIBILITY_ID, "Search"), timeout=6
                            )
                            print("Field located with: ACCESSIBILITY_ID 'Search'")
                        except Exception:
                            # 6) Last resort: the script's original locator.
                            try:
                                search_field = wait_for_element(
                                    driver,
                                    (AppiumBy.CLASS_NAME, "android.widget.EditText"),
                                    timeout=6,
                                )
                                print(
                                    "Field located with: CLASS_NAME 'android.widget.EditText'"
                                )
                            except Exception:
                                # If ALL of them fail, we print a clear message and
                                # let the error bubble up to the general except (we do not swallow it).
                                print(
                                    "Search field not found with any "
                                    "of the tried locators (CLASS_NAME AutoCompleteTextView, "
                                    "XPath EditText | AutoCompleteTextView, ID "
                                    "search_src_text, ACCESSIBILITY_ID 'Buscar'/'Search', "
                                    "CLASS_NAME EditText)."
                                )
                                raise

        # Types a sample query. The device locale is Spanish, so the query must be in
        # Spanish too. In your app you will change the locator and the text.
        search_field.send_keys("batería")

        # Brief pause ONLY so you can see the result on screen (it is not the main wait).
        time.sleep(2)

        # Takes a screenshot and saves it next to this file (evidence of the test).
        screenshot_path = os.path.join(os.path.dirname(__file__), "evidence_test.png")

        # save_screenshot saves the image; True = it was saved correctly.
        saved = driver.save_screenshot(screenshot_path)

        # Reports on the console whether the evidence was generated.
        print(f"Screenshot saved ({saved}): {screenshot_path}")

        # Final success message for whoever runs the script by hand.
        print("Test completed successfully.")

    except Exception as error:
        # If anything fails, it shows the error type and the message (useful for learning to debug).
        print(f"Test failed: {type(error).__name__}: {error}")

        # If the driver got created, try to save a screenshot of the error state.
        if driver:
            # Filename for the failure screenshot.
            error_path = os.path.join(os.path.dirname(__file__), "evidence_error.png")

            # Saves the screen at the moment of the error.
            driver.save_screenshot(error_path)

            # Reports where the failure evidence ended up.
            print(f"Error screenshot: {error_path}")

        # Re-raises the error so Python's exit code is not 0 (failed test).
        raise

    finally:
        # finally ALWAYS runs: on success or on error. Here we close the session.
        if driver:
            # quit() closes the controlled app and releases the device in Appium.
            driver.quit()

            # Confirms on the console that the session was closed (avoids orphan sessions).
            print("Appium session closed.")


# This if makes the test run only when executed directly: python test_mi_app.py
# If another file imports this module, the test will not be launched automatically.
if __name__ == "__main__":
    # Calls the main test case.
    test_open_settings_and_search()
