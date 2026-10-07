# Mobile QA Automation — Practice Portfolio

A portfolio repository of mobile test automation exercises built with **Appium**, **Python**, and an **AI-assisted engineering workflow (OpenCode)**. Each numbered folder is a self-contained practice with its own test script, documentation, and evidence artifacts.

> Goal of this repository: demonstrate professional mobile test automation practices — robust locator strategy, root-cause debugging on physical devices, formal QA acceptance criteria, and disciplined AI-assisted delivery — to QA automation recruiters and engineering teams.

## Practices

| # | Practice | Status | Description |
|---|----------|--------|-------------|
| 01 | [Phase 1: System apps practice](01%20System%20apps%20practice/README.md) | ✅ Verified on a physical Samsung Galaxy A33 (Android 16, One UI) | End-to-end Appium test: open the native Settings app → search for an item, with ordered locator fallback chains, clean-start state handling, and screenshot evidence. |
| 02 | [Phase 2: Sauce Labs E-commerce](02_saucelabs_ecommerce/test_sauce_checkout.py) | ✅ Verified on a physical Samsung Galaxy A33 (Android 16, One UI) | End-to-end add-to-cart flow on the Sauce Labs mobile demo app: catalog → product detail → add to cart → cart-badge assertion, driven by explicit waits and screenshot evidence. |

Each numbered practice documents its full test case — preconditions, Given/When/Then steps, acceptance criteria, and actual results — plus the engineering findings behind it.

## Phase 2: E-commerce End-to-End Automation

Validates a real-world purchase funnel on a **physical device** with Appium: launch the Sauce Labs mobile demo app, open a product, add it to the cart, and assert the cart-badge state. The test runs against an APK installed from a local file (`App/mda-2.3.0-27.apk`) on a Samsung Galaxy A33.

### Test case — TC-AND-002: Add to Cart Flow on Sauce Labs Mobile App

**Preconditions**

- Appium Server 3.8.0 reachable at `http://127.0.0.1:4723`; physical device connected via ADB.
- Local device config: copy `config.example.json` to `config.json` and set your device UDID — the real config is gitignored, so the serial stays off GitHub.
- Clean app state: the session clears app data at start (`noReset=False`), so the cart always begins empty and the badge assertion is deterministic.

**Flow (Given / When / Then)**

1. **Given** the app launches with a forced fresh start, the catalog is loaded when the `Products` header becomes visible.
2. **When** the first product tile (Sauce Labs Backpack) is clicked via its product image view, the product detail screen opens.
3. **Then** the detail screen title matches the expected product.
4. **When** the `Add to cart` button is tapped, the item is added.
5. **Then** the cart badge displays `1`, and a success screenshot is saved (`evidence_sauce_add_to_cart.png`).

**Acceptance criteria**

- Cart badge count equals `1` after a single add.
- Evidence artifact (`evidence_sauce_add_to_cart.png`) is written next to the script.
- Test exits with code `0`. No fixed sleeps: every step is guarded by explicit waits (`WebDriverWait`).

**Actual result:** ✅ Passed — executed end-to-end on the physical device. All steps witnessed, badge asserted to `1`, screenshot captured, clean exit.

### Key engineering finding — clickable surface vs. visible text

In the Sauce Labs demo APK, the product **title `TextView` carries no `onClick` listener** — tapping the title does not open the product. The clickable surface is the tile's **image view** (`id/productIV`). Since the title's resource-id (`titleTV`) and accessibility label (`Product Title`) repeat across every catalog tile, neither can uniquely identify a product. The robust locator strategy is therefore:

| Step | Locator strategy | Verified value |
|---|---|---|
| Open first product | Click the tile **image** (first in document order) | `id/productIV` `[0]` |
| Confirm detail screen | Exact **text** match on the detail title | `UiSelector().resourceId("id/productTV").text("Sauce Labs Backpack")` |
| Add to cart | Unique **accessibility-id** | `content-desc = "Tap to add product to cart"` |
| Assert badge | Unique **resource-id** (exists only when the cart has items) | `id/cartTV` — text `"1"` |

This selector discipline — accessibility-id → unique resource-id → exact text — is applied consistently across both phases.

## Tech stack

- **Language:** Python 3.12
- **Automation:** Appium Server 3.8.0 + UiAutomator2 driver 8.7.0
- **Client:** Appium Python Client v3 (`WebDriverWait`, `expected_conditions`)
- **Device communication:** Android ADB (platform-tools)
- **Evidence:** screenshot artifacts committed per practice

Full prerequisites and step-by-step instructions for Phase 1 live in the [practice README](01%20System%20apps%20practice/README.md); the Phase 2 test case is documented in the section above.

## AI-Assisted Engineering

This repository is developed with an AI-assisted workflow using **OpenCode**, under a strict human-owned quality gate:

1. The AI agent proposes changes (capabilities, locators, error handling).
2. Every change passes a syntax check (`python -m py_compile`).
3. Every change is executed end-to-end on a **physical device** — never accepted from code review alone.
4. The QA engineer verifies results against the acceptance criteria before merging.

No result is reported in this repository without a real run behind it.

## Repository structure

```text
.
├── 01 System apps practice/
│   ├── test_mi_app.py          # Appium test script (English comments)
│   ├── config.example.json     # Device-config template (copy to config.json)
│   ├── README.md               # Full QA documentation + acceptance criteria
│   ├── AGENTS.md               # AI-agent context: environment and locator rules
│   ├── evidence_test.png       # Success evidence
│   ├── evidence_error.png      # Failure evidence
│   └── __pycache__/            # Not tracked (see .gitignore)
├── 02_saucelabs_ecommerce/
│   ├── test_sauce_checkout.py             # TC-AND-002: add-to-cart flow (English comments)
│   ├── evidence_sauce_catalog.png         # Catalog UI dump evidence (locator discovery)
│   ├── evidence_sauce_add_to_cart.png     # Add-to-cart success evidence
│   ├── qr-code.png                        # APK download QR (source reference)
│   ├── config.example.json                # Device-config template (copy to config.json)
│   ├── App/
│   │   └── mda-2.3.0-27.apk               # Sauce Labs mobile demo app under test
│   └── __pycache__/                       # Not tracked (see .gitignore)
├── .gitignore
└── README.md                   # This file
```
