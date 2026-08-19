# TfGB API

Transport for Greater Bandung API.

## Features

- **MJT PIS**: MJT Passenger Information System from `https://mjt.trans.my.id`.

---

## Installation & Running

### 1. Setup Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Development Server

Using the FastAPI CLI:

```bash
fastapi dev main.py
```

Or using Uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Run with Docker

```bash
# Build image locally
docker build -t tfgb-api .

# Run container
docker run -d -p 8000:8000 --name tfgb-api tfgb-api
```

---

## API Endpoints

| Method | Endpoint          | Description                                                                   |
| ------ | ----------------- | ----------------------------------------------------------------------------- |
| `GET`  | `/`               | Service discovery & metadata                                                  |
| `GET`  | `/api/health`     | Service health status                                                         |
| `GET`  | `/api/mjt/buses`  | Get active buses data                                                         |
| `GET`  | `/api/mjt/routes` | Get bus routes data                                                           |
| `GET`  | `/api/mjt/token`  | Get active session tokens (dynamic TTL cache, `?refresh=true` to force renew) |
| `GET`  | `/docs`           | Interactive ReDoc API documentation                                           |

---

## Project Structure

```
├── mjt/
│   ├── __init__.py
│   ├── client.py       # MJT upstream client & session token management
│   ├── router.py       # MJT PIS service routes (/api/mjt/*)
│   └── README.md       # MJT module documentation
├── main.py             # FastAPI entrypoint, middleware, & router registry
├── requirements.txt    # Python dependencies
└── README.md           # Documentation
```

---

Made with 🫰 by a fellow commuter.
