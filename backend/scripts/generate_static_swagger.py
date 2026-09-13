# هذا الملف يولد صفحة Swagger static من OpenAPI الخاص بالتطبيق.

import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
OUTPUT_FILE = BACKEND_DIR / "swagger-static" / "index.html"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app


# ينشئ ملف HTML واحد يمكن رفعه على Shared Hosting.
def generate_static_swagger() -> None:
    openapi_schema = app.openapi()
    schema_json = json.dumps(openapi_schema, ensure_ascii=False, indent=2)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Phishing Email Detector API Documentation</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
  <style>
    body {{
      margin: 0;
      background: #f7f8fa;
    }}
    .topbar {{
      display: none;
    }}
    .static-note {{
      padding: 14px 28px;
      background: #17324d;
      color: #fff;
      font-family: Arial, sans-serif;
      font-size: 14px;
      line-height: 1.5;
    }}
  </style>
</head>
<body>
  <div class="static-note">
    Static API documentation only. This page does not connect to any live backend, and Try it out is disabled.
  </div>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    const spec = {schema_json};

    window.onload = () => {{
      window.ui = SwaggerUIBundle({{
        spec,
        dom_id: "#swagger-ui",
        deepLinking: true,
        supportedSubmitMethods: [],
        presets: [SwaggerUIBundle.presets.apis],
        layout: "BaseLayout"
      }});
    }};
  </script>
</body>
</html>
"""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    generate_static_swagger()
