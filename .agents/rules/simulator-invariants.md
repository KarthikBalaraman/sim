---
description: Critical architectural invariants and coding rules for the Court Booking Revenue Simulator
globs: ["*.py", "*.html", "*.json", "*.md"]
---

# Simulator Invariants & Rules

## 1. Zero External Dependencies
- `server/server.py` MUST strictly use Python 3 standard library modules.
- Under NO circumstance may third-party pip packages (e.g. `requests`, `flask`, `fastapi`, `pydantic`, `pyjwt`) be imported or added.

## 2. No Frontend Build Steps
- All UI is in `client/Simulator.html` and `client/login.html`.
- Styles use Tailwind CSS via CDN.
- Graphs use Chart.js via CDN.
- Do NOT generate or suggest adding `package.json`, Vite, Webpack, or Babel.

## 3. Currency Symbols & Formatting
- **INR**: Symbol `₹` without space (`₹300`).
- **AED**: Symbol `'AED '` with trailing space in text labels (`AED 15`, `AED 200`).
- **Input Group Badges**: Inside input fields, currency badges must be inside a flex container with `.input-prefix`. Never use `absolute` positioning overlaying input fields.

## 4. Input Parsing & Zero-Falsy Bug Prevention
- When parsing numerical inputs (e.g., `startingVenues`, `venueGrowth`, `hoursPerWeek`), `0` is a valid entry.
- All simulation inputs are safely parsed through `getSafeParam()`.

## 5. Configuration Architecture
- Default values and slider bounds for both `INR` and `AED` are maintained in `config/config.json`.
- `server/server.py` exposes them at `/api/config`.
- `client/Simulator.html` fetches this configuration dynamically with embedded fallback.

## 6. Railway & Container Deployment
- Production deployment is configured via `railway.json`, `Dockerfile`, `Procfile`, and `nixpacks.toml`.
- Server binds dynamically to `0.0.0.0:$PORT` and serves health checks at `/api/health`.
- `.dockerignore` must always protect `.env` from inclusion in container images.

## 7. Mandatory Agent & Documentation Synchronization
- **CRITICAL**: Whenever ANY modifications are made to this codebase (endpoints, calculation logic, UI elements, DOM IDs, configuration keys, or styles), the agent MUST synchronously update:
  - `AGENTS.md`
  - `GEMINI.md`
  - `CLAUDE.md`
  - `.cursorrules`
  - `.github/copilot-instructions.md`
  - `.agents/rules/simulator-invariants.md`
  - `README.md`
  - `tests/test_simulator.py`
- Outdated documentation or desynchronized instructions are strictly considered breaking defects.


