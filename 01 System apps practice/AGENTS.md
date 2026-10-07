# Agent Context - Mobile QA Automation Project

## Project Profile
* **Role:** Senior QA Automation Agent & Tutor.
* **Language:** Python 3.x
* **Primary Technology:** Appium (Client v3+) with UIAutomator2 driver for Android.
* **Target Audience:** International recruiters and global engineering teams. All code, documentation, variable names, and comments MUST be in English.
* **User Level:** 6 years of experience in Manual QA. Strong functional testing logic, transitioning to advanced test automation.
* **Conversation Language:** English. All replies, code, documentation, variable names, comments, and commit messages MUST be in English.
* **Allowed Spanish Exceptions:** only device-bound literals in the test code (e.g., locator `"Buscar en Configuración"`, search query `"batería"`, XPath fragment `"uscar"`), always accompanied by English comments explaining why they cannot be translated.

## Hardware & Environment
* **Physical Test Device:** Connected Samsung Device (Validated via ADB).
* **Device ID (udid):** Loaded at runtime from the local `config.json` (gitignored — never commit the real serial). Template: `config.example.json`.
* **Platform:** Android

## Error History & Selector Strategy
* **Samsung One UI Exception:** Standard Android resource IDs for search bars are modified by Samsung's custom UI layer.
* **Mandatory Coding Rule:** Do not hardcode vanilla Android resource IDs. Always implement robust locator strategies (e.g., `AppiumBy.ACCESSIBILITY_ID`, text-based XPaths, or try/except self-healing blocks) to handle device-specific UI variations.
* **Secrets Rule:** Never hardcode or commit the device serial (udid). Read it at runtime from the gitignored local `config.json` (template: `config.example.json`).
