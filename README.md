# Mobile QA Automation — Practice Portfolio

A portfolio repository of mobile test automation exercises built with **Appium**, **Python**, and an **AI-assisted engineering workflow (OpenCode)**. Each numbered folder is a self-contained practice with its own test script, documentation, and evidence artifacts.

> Goal of this repository: demonstrate professional mobile test automation practices — robust locator strategy, root-cause debugging on physical devices, formal QA acceptance criteria, and disciplined AI-assisted delivery — to QA automation recruiters and engineering teams.

## Practices

| # | Practice | Status | Description |
|---|----------|--------|-------------|
| 01 | [System apps practice](01%20System%20apps%20practice/README.md) | ✅ Verified on a physical Samsung Galaxy A33 (Android 16, One UI) | End-to-end Appium test: open the native Settings app → search for an item, with ordered locator fallback chains, clean-start state handling, and screenshot evidence. |
| 02 | Saucelabs Ecommerce | 🚧 Planned | E-commerce mobile test automation practice. |

Each practice README contains the full test case documented as a formal QA artifact (preconditions, Given/When/Then steps, acceptance criteria, actual results) plus the engineering findings behind it.

## Tech stack

- **Language:** Python 3.12
- **Automation:** Appium Server 3.8.0 + UiAutomator2 driver 8.7.0
- **Client:** Appium Python Client v3 (`WebDriverWait`, `expected_conditions`)
- **Device communication:** Android ADB (platform-tools)
- **Evidence:** screenshot artifacts committed per practice

Full prerequisites and step-by-step instructions live in each practice README (see [01 System apps practice](01%20System%20apps%20practice/README.md)).

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
│   ├── README.md               # Full QA documentation + acceptance criteria
│   ├── AGENTS.md               # AI-agent context: environment and locator rules
│   ├── evidence_test.png       # Success evidence
│   ├── evidence_error.png      # Failure evidence
│   └── __pycache__/            # Not tracked (see .gitignore)
├── 02 Saucelabs Ecommerce/     # Planned practice
├── .gitignore
└── README.md                   # This file
```
