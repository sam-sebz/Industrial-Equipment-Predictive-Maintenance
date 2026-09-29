# TRD

## Architecture
Browser -> FastAPI -> validation -> persisted ML model -> risk threshold -> SQLite -> dashboard.

## Stack
Python, FastAPI, pandas, scikit-learn, SQLite, HTML, CSS and JavaScript.

## API
GET /api/health
GET /api/metrics
POST /api/predict
GET /api/predictions

## Testing
Held-out model evaluation, threshold tuning and API smoke tests.
