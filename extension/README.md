# Nexus Chrome Extension

> **The extension ships in real API mode** (`DEMO_MODE: false` in `config.js`). Start the Nexus backend before scanning. Demo mode remains available for UI-only testing; see [Demo Mode](#demo-mode).

Nexus Chrome Extension is a lightweight browser client for Nexus, our phishing detection system. It lets you check suspicious content while you browse, straight from Chrome's right-click menu:

* **Select text** on a web page, right-click, and choose **Scan Text with Nexus**.
* **Right-click a link** and choose **Scan URL with Nexus**.

The extension sends only what you selected to the Nexus backend, then shows the backend's answer (classification, risk score, and reasons) in a small result window. From there, **View Full Analysis** opens the main Nexus web application with the scanned URL or text already filled in and analyzed.

The extension does not detect phishing itself. In real mode, all analysis is done by the Nexus backend. In demo mode, results are pre-written examples.

## How to Use

### Scan Text

1. Open any regular web page (`http` or `https`).
2. Select the text you want to check, for example:
   *"Your account has been suspended. Click here immediately to verify your account."*
3. Right-click the selection and choose **Scan Text with Nexus**.
4. A Nexus window opens, shows **Nexus is analyzing...**, and then displays the result.

### Scan URL

1. Right-click a link on a web page.
2. Choose **Scan URL with Nexus**.
3. The **link you right-clicked** is analyzed (not the page you are on).

### The Result Window

```text
NEXUS  Analysis Result

Scanned link
https://suspicious-example.com/login

⚠ Phishing

Risk Score                  92%
████████████████████░░

Reasons
• (reasons returned by the backend)

For more details, visit Nexus.
[ View Full Analysis ]
```

* The classification is shown exactly as the backend returns it. `Phishing` is red, `Legitimate` is green, and any other classification the backend may add is shown as-is in a neutral style.
* **View Full Analysis** opens the main Nexus web application in a new tab, with exactly what you scanned already filled in and analyzed (see [View Full Analysis](#view-full-analysis)).
* If something goes wrong (for example the backend is offline), a friendly message is shown, with **Try Again** when retrying can help.

Clicking the Nexus icon in the Chrome toolbar shows a short how-to, whether the Nexus backend is reachable, and an **Open Nexus** button.

## View Full Analysis

**View Full Analysis** opens the Nexus web app with the exact scanned input in the address, and the web app fills in the matching input and runs its normal analysis:

| You scanned | The extension opens | The web app then |
| --- | --- | --- |
| A link (**Scan URL with Nexus**) | `http://localhost:5173/?url=<scanned URL>` | Switches to the **URL** input type, fills in the link, and analyzes it. |
| Selected text (**Scan Text with Nexus**) | `http://localhost:5173/?text=<scanned text>` | Switches to the **Text** input type, fills in the text, and analyzes it. |

For example, scanning `https://example.com/login` opens `http://localhost:5173/?url=https%3A%2F%2Fexample.com%2Flogin`.

* The value is percent-encoded (`encodeURIComponent`), so characters such as `&`, `#`, `%`, spaces, quotes, and non-Latin text arrive exactly as scanned.
* The web app uses its existing analysis code and backend API. Nothing is duplicated, and no results are faked.
* Once the web app has read the parameter it removes it from the address bar, so reloading the page does not analyze the input again.
* **Very long input opens the web app empty.** Web servers reject very long addresses (the Vite dev server answers HTTP 431 above about 16,000 characters, and many servers stop at 8,000), and non-Latin text is encoded at up to 9 characters per letter (Arabic: about 6). If the address would exceed `MAX_DEEP_LINK_LENGTH` (8,000), the extension opens the plain home page instead and the result window says so; paste the text there to analyze it. Typical English selections and normal URLs fit.
* The toolbar popup's **Open Nexus** button opens the plain home page with no parameters.
* **The web app always uses the real backend.** In Demo Mode the extension's own result is a simulated example, but the full analysis in the web app is a real one, so it needs the backend running (and its scores can differ from the demo result).
* **The backend must allow the web app's address.** The default `CORS_ORIGINS` setting already allows `http://localhost:5173` and `http://127.0.0.1:5173`. Add the deployed web-app origin when hosting it elsewhere.

## Demo Mode

Demo Mode is a **temporary testing mode** for trying the complete Chrome Extension experience (right-click menus, loading state, results, errors, "View Full Analysis") **without the Nexus backend**. It needs no server, no API connection, no CORS setup, and no ML model.

* Results come from a small set of **fake, pre-written examples** in `demo-data.js`. They are **not** real security decisions.
* **No network request is made.** The backend can be completely offline.
* Demo Mode is **not a phishing detector**. It is a lookup table: if the input is exactly one of the demo test values below, the matching example is returned; anything else gets the same generic demo result. Nothing inspects or scores the content.
* Demo Mode is clearly marked, so demo results cannot be mistaken for real ones: a **DEMO MODE** badge in the result window header and the toolbar popup, a "simulated, not a real security analysis" note on every result, and a **DEMO** badge on the toolbar icon.
* A short "Nexus is analyzing..." delay (about 0.8 seconds) is simulated so the loading state can be tested.

### Try Demo Mode

1. Open `extension/config.js` and temporarily change it to `DEMO_MODE: true`.
2. Open `chrome://extensions/` in Chrome.
3. Enable **Developer mode** (top-right).
4. Click **Load unpacked** and select the `extension` folder (the one containing `manifest.json`).
5. Open a regular web page that contains the demo text and links (see [a simple test page](#a-simple-test-page) below).
6. **Select text**, right-click, and choose **Scan Text with Nexus**.
7. **Right-click a link** and choose **Scan URL with Nexus**.

If you change `config.js` later, click the reload icon on the Nexus card in `chrome://extensions/`.

### Demo Test Inputs

All values are clearly fictional. `.test` is a reserved domain that never points to a real website.

**Selected text** (matched ignoring upper/lower case and extra spaces):

| Select this text | Demo result |
| --- | --- |
| `Your account has been suspended. Click here immediately to verify your account.` | Phishing, 87% |
| `Your account has been suspended. Please verify your account immediately.` | Phishing, 87% |
| `Welcome to our official website. Learn more about our services.` | Legitimate, 5% |
| `Welcome to our website. Learn more about our services.` | Legitimate, 5% |
| `DEMO_ERROR` | Error: "Unable to analyze this input." with **Try Again** |
| anything else | Generic "Demo Result" (neutral, score N/A) |

**Right-clicked links** (matched by host name, so any path works):

| Link | Demo result |
| --- | --- |
| `https://demo-phishing.test/login` | Phishing, 92% |
| `https://example-phishing.test/login` | Phishing, 92% |
| `https://demo-safe.test/` | Legitimate, 5% |
| `https://demo-error.test/` | Error: "Unable to analyze this input." with **Try Again** |
| any other link | Generic "Demo Result" (neutral, score N/A) |

### A Simple Test Page

The extension only scans text selected on regular `http`/`https` pages (not `file://`), so serve a small test page locally. Save this as `demo.html`:

```html
<p>Your account has been suspended. Click here immediately to verify your account.</p>
<p>Welcome to our official website. Learn more about our services.</p>
<p>DEMO_ERROR</p>
<ul>
  <li><a href="https://demo-phishing.test/login">Verify your account</a></li>
  <li><a href="https://demo-safe.test/">Our official site</a></li>
  <li><a href="https://demo-error.test/">Error example</a></li>
</ul>
```

Then, in the folder containing it, run `python -m http.server 8080` and open `http://localhost:8080/demo.html`. (You can also select text on any regular website.)

### Switching to Real API Mode

1. In `extension/config.js`, set `DEMO_MODE: false`.
2. Start the Nexus backend (see [How to Run the Extension Locally](#how-to-run-the-extension-locally)).
3. Reload the extension in `chrome://extensions/`.

The DEMO MODE indicators disappear, the toolbar popup shows whether the backend is reachable, and scans use `POST /api/v1/analyze/text` and `POST /api/v1/analyze/url`. The real API code is unchanged and always available; `DEMO_MODE` only switches the data source.

## How to Run the Extension Locally

The steps below cover real API mode. For Demo Mode you can skip steps 2 and 3 (no backend and no web app needed).

### 1. Clone the Repository

Clone the Nexus repository and switch to the extension branch:

```bash
git clone <repository-url>
cd <project-folder>
git checkout feature/nexus-extension
```

### 2. Start the Nexus Backend

The extension needs the Nexus backend. By default it expects it at `http://localhost:8000`, the same address the Nexus web app uses.

The backend lives in the `backend/` folder (currently on the `feature/backend` branch). From that folder:

```bash
pip install -r requirements.txt
uvicorn app.main:app --port 8000
```

Check that it is running by opening `http://localhost:8000/api/v1/health`.

### 3. Start the Nexus Web App (for "View Full Analysis")

From the `frontend/` folder:

```bash
npm install
npm run dev
```

The web app is then available at `http://localhost:5173`.

### 4. Open Chrome Extensions

Open Google Chrome and navigate to:

```text
chrome://extensions/
```

### 5. Enable Developer Mode

Enable **Developer mode** from the top-right corner of the Chrome Extensions page.

### 6. Load the Extension

Click:

```text
Load unpacked
```

Select the `extension` folder from the Nexus project (the folder that contains `manifest.json`).

### 7. Try It

Open a web page, select some text or right-click a link, and use the **Nexus** entry in the right-click menu. Chrome groups the two Nexus actions under a single **Nexus** menu when both apply.

After changing any file in the `extension` folder, click the reload icon on the Nexus card in `chrome://extensions/`.

## Configuration

All settings live in one file, `config.js`:

```js
export const NEXUS_CONFIG = Object.freeze({
  DEMO_MODE: false,                        // true = fake demo results, no network; false = real backend
  API_BASE_URL: "http://localhost:8000",   // Nexus backend
  NEXUS_APP_URL: "http://localhost:5173",  // main Nexus web app ("View Full Analysis")
  REQUEST_TIMEOUT_MS: 15000,
  MAX_TEXT_LENGTH: 5000,                   // longest text selection that can be scanned
  MAX_DEEP_LINK_LENGTH: 8000,              // longest web address "View Full Analysis" may open
});
```

| Setting | What it does | If you change it |
| --- | --- | --- |
| `DEMO_MODE` | `false` (default): real Nexus backend. `true`: simulated results from `demo-data.js`, with no network requests. | Reload the extension. |
| `API_BASE_URL` | Address of the Nexus backend. | Also update `host_permissions` in `manifest.json` to the same origin (for example `"https://api.example.com/*"`), then reload the extension. |
| `NEXUS_APP_URL` | The main Nexus web app opened by **View Full Analysis** and **Open Nexus**. | Just reload the extension. Use your deployed URL when there is one. |
| `REQUEST_TIMEOUT_MS` | How long to wait for the backend. | Just reload. |
| `MAX_TEXT_LENGTH` | Longest selection accepted (same limit as the web app's text box). | Just reload. |
| `MAX_DEEP_LINK_LENGTH` | Longest web address **View Full Analysis** may open. Longer input opens the web app empty (see [View Full Analysis](#view-full-analysis)). | Just reload. Servers reject very long addresses, so raise it only if yours allows it. |

Do not put API keys or other secrets in the extension: anything inside it can be read by the user.

## How the Extension Talks to the Backend

This section applies to real API mode (`DEMO_MODE: false`). In demo mode the extension makes no network requests at all.

The extension uses the same API as the Nexus web app.

| Action | Request |
| --- | --- |
| Scan Text with Nexus | `POST {API_BASE_URL}/api/v1/analyze/text` with `{ "text": "<selected text>" }` |
| Scan URL with Nexus | `POST {API_BASE_URL}/api/v1/analyze/url` with `{ "url": "<right-clicked link>" }` |

Response (`200`):

```json
{
  "input_type": "url",
  "classification": "Phishing",
  "risk_score": 75,
  "reasons": ["..."]
}
```

* `classification` is displayed as returned. It must be a non-empty string, otherwise an "unexpected response" error is shown.
* `risk_score` (0-100) is shown as a percentage. If it is missing or out of range, "N/A" is shown.
* `reasons` are shown as a list, as plain text. If there are none, the window says so instead of inventing any.

The backend only accepts `http` and `https` URLs, so other links (`mailto:`, `javascript:`, `chrome://`, `file://`, ...) are refused by the extension before anything is sent.

### Errors

| Situation | Message |
| --- | --- |
| Backend unreachable / network error | Unable to connect to the Nexus analysis service. |
| No response in time | The Nexus analysis service took too long to respond. Please try again. |
| HTTP 5xx | The Nexus analysis service returned an error. Please try again later. |
| HTTP 4xx (including 422) | The Nexus analysis service could not process this content. |
| Invalid JSON or missing classification | The Nexus analysis service returned an unexpected response. |
| Empty selection | No text is selected. Select some text and try again. |
| Selection longer than `MAX_TEXT_LENGTH` | The selected text is too long to scan... |
| Text selected on a non-`http(s)` page (`chrome://`, `file://`, extension pages) | Nexus can only scan text selected on regular web pages (http or https). |
| Link that is not `http(s)` | This link cannot be scanned. Nexus supports http and https links only. |
| Demo error input (demo mode only) | Unable to analyze this input. |

### CORS

No backend CORS change is needed. The manifest lists the backend in `host_permissions`, and Chrome allows the extension to call hosts it has permission for without CORS restrictions. (The backend's `CORS_ORIGINS` setting only applies to normal web pages, such as the Nexus web app.)

## Permissions

| Permission | Why |
| --- | --- |
| `contextMenus` | Adds **Scan Text with Nexus** (shown when text is selected) and **Scan URL with Nexus** (shown on links) to the right-click menu. |
| `host_permissions` (`http://localhost:8000/*`) | Lets the extension call the Nexus backend. Only used in real API mode; in demo mode nothing is called. |

The extension does not request `tabs`, `activeTab`, `history`, `cookies`, `storage`, `bookmarks`, or `webRequest`, and it does not inject scripts into websites or read page content.

## Privacy

* In **demo mode** everything stays local: the selected text and links are compared with the demo test values inside the extension and are never sent anywhere.
* Scanning only happens when **you** choose a Nexus menu item.
* For text, only the text you selected is sent. For links, only the link you right-clicked is sent (including its query string, so avoid scanning links that contain private tokens).
* No cookies or credentials are sent, no page content is read, and nothing is sent to third-party services.
* Nothing is stored. Scan data is kept in memory only while its result window is open. There is no scan history and no use of browser storage.
* When you click **View Full Analysis**, the scanned link or text is placed in the Nexus web app's address (`?url=` / `?text=`) so it can show the full analysis. Because it is part of a web address, it can appear in Chrome's browsing history and in web server logs. Nexus does this only when you click that button, and the web app removes the parameter from the address bar right after reading it. Avoid scanning links or text that contain secrets.
* Text and reasons from the backend are displayed as plain text and never as HTML.

## Architecture

```text
Chrome Browser (right-click)
      |
      v
Nexus Chrome Extension (background service worker)
      |
      |  analyzeText() / analyzeUrl()   (api.js, switched by DEMO_MODE in config.js)
      |
 ┌────┴───────────────┐
 |                    |
DEMO MODE          REAL API MODE
(default)          (DEMO_MODE: false)
 |                    |
 v                    v
demo-data.js       POST /api/v1/analyze/text   or   /url
(local, fake,          |
 no network)           v
 |                 Nexus Backend API -> Phishing Detection System
 |                    |
 └────────┬───────────┘
          v
   Analysis Result
          |
          v
Nexus Chrome Extension (result window)
          |
          v
User  ->  "For more details, visit Nexus."  ->  View Full Analysis  ->  Nexus web app
```

## Project Structure

```text
extension/
├── manifest.json     Manifest V3 configuration and permissions
├── config.js         DEMO_MODE switch, backend address, web app address, timeout, text limit
├── api.js            analyzeText()/analyzeUrl(): picks demo data or the real backend (no detection logic)
├── demo-data.js      Fake demo results for UI testing (no network, not a detector)
├── background.js     Service worker: right-click menus, validation, scan flow, result window
├── result.html/js    The result window (loading, result, errors, View Full Analysis)
├── popup.html/js     Toolbar popup: how-to, DEMO MODE / backend status, Open Nexus
├── styles.css        Shared styles (light and dark)
└── assets/
    └── nexus-logo.png
```

## Current Limitations

* **Demo Mode is on by default and its results are fake.** Turn it off (`DEMO_MODE: false`) to use the backend.
* In real mode, the backend analysis is currently a temporary placeholder (it returns a fixed result for every input) until the final machine learning model is connected. The extension shows real results automatically once the backend does.
* **View Full Analysis** needs the web app to be running and the backend to allow its address (see [View Full Analysis](#view-full-analysis)). Long non-Latin selections (for example Arabic text over about 1,400 characters) are too long to pass in a web address, so they open the web app empty (see above).
* Scans opened from **View Full Analysis** also appear in the web app's Analysis History, like any scan made in the web app.
* Text can only be scanned when selected on regular `http`/`https` pages. Text selected on local files (`file://`) or browser pages cannot be scanned. Links on such pages can still be scanned.
* Selections are limited to `MAX_TEXT_LENGTH` characters (5,000 by default).
* In real mode, the backend must be running and reachable at `API_BASE_URL`.
* The extension is loaded unpacked for development and is not published to the Chrome Web Store.

## Future Features

These are not implemented yet:

* Automatic website scanning
* Warning page for suspicious websites
* Scanning links inside webpages automatically
* Webmail / email analysis
* Scan history, notifications, and settings

## Troubleshooting

* **The Nexus menu items do not appear.** Text scanning only appears when text is selected, and URL scanning only appears when you right-click a link. Chrome does not show extension menu items on some pages (for example `chrome://` pages and the Chrome Web Store). After loading or reloading the extension, refresh the page you are testing on.
* **Every scan shows a "Demo Result" or the same fake answers.** That is Demo Mode (see the **DEMO MODE** badge). Only the inputs in [Demo Test Inputs](#demo-test-inputs) give Phishing/Legitimate/error examples; set `DEMO_MODE: false` for real analysis.
* **"Unable to connect to the Nexus analysis service."** (real mode only) Make sure the backend is running, and that `API_BASE_URL` in `config.js` and `host_permissions` in `manifest.json` both point to it. Reload the extension after changing them. The toolbar popup shows whether the backend is reachable.
* **"View Full Analysis" shows an error page.** Start the web app (`npm run dev` in `frontend/`) or set `NEXUS_APP_URL` in `config.js` to where it is running.
* **"View Full Analysis" opens the web app but it says "Unable to reach the analysis service."** The backend is not running, or it does not allow the web app's address. Add the web app to the backend's `CORS_ORIGINS` (for example `http://localhost:5173`) and restart the backend.
* **Nexus does not appear after "Load unpacked".** Make sure you selected the `extension` folder itself (the one containing `manifest.json`), and check for errors on the Nexus card in `chrome://extensions/`.
