# API Quick Reference

## GET /health
Returns service health.

## GET /api/geocode?name=<city>
Returns geocoded city candidates.

## GET /api/weather?latitude=<lat>&longitude=<lon>
Returns current and hourly forecast fields.

## POST /api/chat
Request:
```json
{"question":"Will rain affect my crop spraying?","latitude":30.901,"longitude":75.8573,"role":"farmer"}
```
Response includes `answer`, `evidence`, `actions`, `risk`, `confidence`, `source`.

## POST /api/alerts/check
Runs the same deterministic risk engine as an alert check.
