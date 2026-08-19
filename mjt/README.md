# MJT (Mitra Juang Trans) Service Module

This module encapsulates all client logic, session management, and API routes for the **MJT Passenger Information System (PIS)**.

Upstream service: [https://mjt.trans.my.id](https://mjt.trans.my.id)

---

## 📁 Module Overview

```
mjt/
├── __init__.py     # Package exports (mjt_client, router)
├── client.py       # Async HTTP client, session extraction, & TTL cache
├── router.py       # FastAPI APIRouter mounted at /api/mjt
└── README.md       # Module documentation
```

---

## ⚙️ Architecture & Session Lifecycle

The MJT web portal employs a session verification mechanism requiring three key components:

1. **`mjt` Cookie**: Session identifier cookie set by the web portal.
2. **`X-TOKEN` Cookie**: Authentication token cookie.
3. **`pisNonce`**: Dynamic nonce extracted from the JavaScript configuration of the portal HTML (`https://mjt.trans.my.id/pis/web`).

### How `MJTClient` Works (`mjt/client.py`)

- **Dynamic TTL & In-Memory Caching**:
  Extracts the dynamic `pisNonceTtl` from upstream HTML (e.g. `pisNonceTtl: 300`) and caches tokens in memory for that exact duration. Subsequent calls to `/api/mjt/token` return cached values without querying the upstream portal.
- **On-Demand Auto-Refresh**:
  When 300 seconds elapse, tokens expire. A fresh session is only fetched when a new request arrives (e.g. for buses, routes, or tokens).
- **Automatic Recovery**:
  If the upstream returns a `401`, `403`, or invalid nonce rejection, `MJTClient` immediately flushes the cookie jar, acquires fresh tokens, and retries the request once automatically.
- **Async & Non-Blocking**:
  Built on `httpx.AsyncClient` with `asyncio.Lock()` to prevent race conditions during token refresh.

---

## 📡 Endpoints (`mjt/router.py`)

All routes are prefixed with `/api/mjt`.

### 1. `GET /api/mjt/token`

Retrieves current session tokens and nonce.

- **Query Parameters**:
  - `refresh` _(boolean, optional, default=false)_: Pass `?refresh=true` to force token renewal from upstream immediately.
- **Sample Response**:
  ```json
  {
    "pis_nonce": "cjU4YmhxZ3A4NnZicm5nZGZiMTdndTNuNnQxazJpMmF8...",
    "mjt_cookie": "r58bhqgp86vbrngdfb17gu3n6t1k2i2a",
    "xtoken_cookie": "3ae3496b26bc166a755b0ca6123ee4c5",
    "expires_in": 299,
    "cached": true
  }
  ```

---

### 2. `GET /api/mjt/buses`

Fetches real-time bus locations, headings, velocity, and telemetry.

- **Upstream Ajax**: `https://mjt.trans.my.id/pis/ajax/json_getInitialBuses`
- **Sample Response**:
  ```json
  {
    "status": 1,
    "message": "Success",
    "data": [
      {
        "acc": "1",
        "ago": "98",
        "battery_percent": "1",
        "company_nm": "Teman Bus",
        "direction": "344",
        "gap": "26",
        "gps_sn": "869066064765085",
        "gps_time": "2026-08-19 10:41:24",
        "group_nm": "BTS",
        "id": "869066064765085",
        "ip": "114.122.68.242",
        "jenroute": "BTS",
        "kor": "FD-1",
        "lat": -6.919581,
        "lon": 107.609893,
        "name": "FD-1 04",
        "new_shel_t": "0041515",
        "nopol": "D 1969 BD",
        "old_shel_t": "0041703",
        "port": "10351",
        "pref": "63",
        "protocol": "GT06-A0",
        "route_id": "778",
        "speed": 14,
        "stime": "2026-08-19 10:41:24",
        "toward": "Simpang Soetta Kiaracondong 2"
      }
    ]
  }
  ```

---

### 3. `GET /api/mjt/routes`

Fetches route geometries, coordinate offsets, and shelter lists.

- **Upstream Ajax**: `https://mjt.trans.my.id/pis/ajax/json_getRoutes`
- **Sample Response**:
  ```json
  {
    "status": 1,
    "message": "Success",
    "data": [
      {
        "id": "2122",
        "route_id": "778",
        "kor": "FD-1",
        "color": "#22b473",
        "points": "nrki@gr~oSNnAP...",
        "route": "Simpang Soetta Kircon - Pasar Baru ABC",
        "origin": "Simpang Soetta Kiaracondong 2",
        "toward": "Pasar Baru ABC",
        "jam_ops": "04:30 - 20:00",
        "is_ops": "1",
        "shelters": [
          {
            "latitude": -6.9475,
            "longitude": 107.635278,
            "nama_selter": "SPBU Simpang Buah Batu Soekarno Hatta",
            "kategori": "Shelter"
          }
        ],
        "points_offset": "prki@gr~oS?p@X`..."
      }
    ]
  }
  ```

---

## 💻 Programmatic Usage

You can import and use `mjt_client` directly in other Python scripts or background tasks:

```python
import asyncio
from mjt.client import mjt_client

async def main():
    # Fetch buses directly
    buses = await mjt_client.get_initial_buses()
    print("Active Buses:", len(buses.get("data", [])))

    # Fetch routes directly
    routes = await mjt_client.get_routes()
    print("Routes:", len(routes.get("data", [])))

    # Cleanup connection pool
    await mjt_client.close()

if __name__ == "__main__":
    asyncio.run(main())
```
