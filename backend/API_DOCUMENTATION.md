# Phishing Email Detector API Documentation

Backend API for the Nexus team graduation project.

Current analysis responses use clear mock placeholder logic only. They are not Machine Learning predictions yet.

## Local API Links

- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Static Swagger

Public static documentation is available in:

`swagger-static/index.html`

This file is documentation only. It does not call localhost or any deployed backend, and Try it out is disabled.

To refresh it after changing routes, schemas, validation, or responses:

```bash
python scripts/generate_static_swagger.py
```

Run the command from inside the `backend` folder.

## Endpoints

### GET `/api/v1/health`

Purpose: Check that the backend is running.

Request: No request body.

Response:

```json
{
  "status": "ok",
  "service": "Phishing Email Detector API",
  "version": "1.0.0"
}
```

Errors:

```json
{
  "detail": "Internal server error"
}
```

Status codes: `200`, `500`

### POST `/api/v1/analyze/email`

Purpose: Analyze an email using its subject and body.

Request:

```json
{
  "subject": "string",
  "body": "string"
}
```

Response:

```json
{
  "input_type": "email",
  "classification": "Phishing",
  "risk_score": 85,
  "reasons": [
    "Mock indicator: final ML model is not connected yet",
    "Mock indicator: temporary backend response for API integration"
  ]
}
```

Status codes: `200`, `422`, `500`

Validation error response:

```json
{
  "detail": "Validation error",
  "errors": []
}
```

### POST `/api/v1/analyze/url`

Purpose: Analyze a single URL.

Request:

```json
{
  "url": "https://example.com/login"
}
```

Response:

```json
{
  "input_type": "url",
  "classification": "Phishing",
  "risk_score": 75,
  "reasons": [
    "Mock indicator: final ML model is not connected yet",
    "Mock indicator: temporary backend response for API integration"
  ]
}
```

Status codes: `200`, `422`, `500`

Validation error response:

```json
{
  "detail": "Validation error",
  "errors": []
}
```

### POST `/api/v1/analyze/text`

Purpose: Analyze plain text.

Request:

```json
{
  "text": "string"
}
```

Response:

```json
{
  "input_type": "text",
  "classification": "Phishing",
  "risk_score": 65,
  "reasons": [
    "Mock indicator: final ML model is not connected yet",
    "Mock indicator: temporary backend response for API integration"
  ]
}
```

Status codes: `200`, `422`, `500`

Validation error response:

```json
{
  "detail": "Validation error",
  "errors": []
}
```

## Uploading Static Swagger To Shared Hosting

1. Open the hosting File Manager.
2. Open the domain or subdomain folder.
3. Upload `backend/swagger-static/index.html`.
4. Open the public URL in the browser.
5. Confirm the Swagger documentation appears.
