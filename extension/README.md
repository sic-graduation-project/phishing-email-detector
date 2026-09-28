# Nexus Chrome Extension

The extension scans selected text or links with the production Nexus phishing API.

## Install

1. Open `chrome://extensions/`.
2. Enable **Developer mode**.
3. Choose **Load unpacked** and select this `extension` folder.
4. Reload the extension after changing `config.js`.

## Use

- Select text, right-click it, and choose **Scan Text with Nexus**.
- Right-click a link and choose **Scan URL with Nexus**.
- Choose **View Full Analysis** to open the same input in the Nexus web app.

Production endpoints are defined once in `config.js`; `manifest.json` grants access to the API origin. Demo fixtures remain available for explicit local UI testing by changing `DEMO_MODE` to `true`, but production defaults to the real analyzer.

Do not put API keys or secrets in extension files because installed extension source is visible to users.
