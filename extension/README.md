# Nexus Chrome Extension

Nexus Chrome Extension is a browser extension designed to help users detect potentially malicious or phishing websites directly from Google Chrome.

The extension connects to the Nexus backend API to analyze the current website URL and display the analysis result to the user.

## How to Use

1. Open Google Chrome.
2. Open the website you want to check.
3. Click the **Nexus** extension icon from the Chrome Extensions menu.
4. Start the website scan.
5. The extension sends the current website URL to the Nexus backend.
6. The analysis result is displayed in the extension.

The result may include:

* Classification: **Legitimate** or **Phishing**
* Risk Score
* Reasons for the classification

## How to Run the Extension Locally

### 1. Clone the Repository

Clone the Nexus repository and switch to the extension branch:

```bash
git clone <repository-url>
cd <project-folder>
git checkout feature/nexus-extension
```

### 2. Open Chrome Extensions

Open Google Chrome and navigate to:

```text
chrome://extensions/
```

### 3. Enable Developer Mode

Enable **Developer mode** from the top-right corner of the Chrome Extensions page.

### 4. Load the Extension

Click:

```text
Load unpacked
```

Select the `extension` folder from the Nexus project.

### 5. Run the Extension

After loading the extension, the Nexus icon should appear in the Chrome Extensions list.

Pin the extension if needed, then click the Nexus icon to use it.

## Architecture

The Chrome Extension acts as a client for the Nexus backend.

```text
Chrome Browser
      |
      v
Nexus Chrome Extension
      |
      v
Nexus Backend API
      |
      v
Phishing Detection System
      |
      v
Analysis Result
```

The phishing classification and risk score are determined by the backend. The extension is responsible for collecting the current website URL, sending it to the API, and displaying the returned result.

## Current Scope

The initial version focuses on:

* Scanning the current website URL
* Sending the URL to the Nexus backend
* Displaying the classification
* Displaying the risk score
* Displaying analysis reasons

Additional features may be added in future versions.
