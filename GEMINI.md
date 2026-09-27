# GEMINI.md — Antigravity & Gemini Workspace Instructions

This repository contains the **Court Booking Revenue Simulator**, a dual-currency (INR / AED) interactive revenue modeler with a zero-dependency Python 3 gatekeeper server.

For comprehensive architectural details, formulas, and workflows, always consult [AGENTS.md](file:///c:/Code/simulator/AGENTS.md).

---

## Core Operational Invariants for AI Agents

1. **Zero External Python Dependencies**:
   - `server/server.py` uses strictly Python 3 standard library (`http.server`, `urllib`, `hmac`, `hashlib`, `json`, `base64`, `time`, `os`).
   - **NEVER** install or import external pip packages (`requests`, `flask`, `fastapi`, `pyjwt`, etc.).

2. **No Frontend Build Pipeline**:
   - `client/Simulator.html` and `client/login.html` are standalone vanilla HTML/JS applications.
   - Styling: Tailwind CSS via CDN (`https://cdn.tailwindcss.com`).
   - Charts: Chart.js via CDN (`https://cdn.jsdelivr.net/npm/chart.js`).
   - **NEVER** add `package.json`, Vite, Webpack, or npm tooling.

3. **Currency Spacing & Input Alignment**:
   - **INR (`₹`)**: No space (`₹300`).
   - **AED (`AED `)**: Always include a trailing space in text labels (`AED 15`, `AED 200`).
   - **Input Prefix Badges**: Currency symbols inside numeric inputs must use the **Flexbox Input Group pattern** (`.input-prefix`). Never use absolute positioning over input text, which causes multi-character symbols like `AED` to overlap numbers.

4. **Zero-Falsy Input Protection**:
   - In `calculate()` and client scripts, never use `parseInt(val) || default` because `0` is a valid entry (e.g. `startingVenues = 0`, `venueGrowth = 0`).
   - All inputs are read safely through `getSafeParam()`.

5. **Server Configuration Centralization**:
   - Default values, pipeline parameters, model levers, and slider bounds are defined in `config/config.json`.
   - Served via `GET /api/config` in `server/server.py`.
   - `client/Simulator.html` loads this on startup with built-in offline fallback.

6. **Mandatory Agent & Documentation Synchronization**:
   - **CRITICAL**: Whenever you make ANY change to this codebase (features, routes, DOM IDs, formulas, config schemas, or UI elements), you MUST synchronously update:
     - [AGENTS.md](file:///c:/Code/simulator/AGENTS.md)
     - [GEMINI.md](file:///c:/Code/simulator/GEMINI.md)
     - [CLAUDE.md](file:///c:/Code/simulator/CLAUDE.md)
     - [.cursorrules](file:///c:/Code/simulator/.cursorrules)
     - [.github/copilot-instructions.md](file:///c:/Code/simulator/.github/copilot-instructions.md)
     - [.agents/rules/simulator-invariants.md](file:///c:/Code/simulator/.agents/rules/simulator-invariants.md)
     - [README.md](file:///c:/Code/simulator/README.md)
     - `tests/test_simulator.py`
   - Outdated agent instructions or stale documentation are treated as breaking defects.

---

## Quick Commands

- **Run Server**: `python server/server.py` (Default: `http://localhost:8000/`)
- **Run Tests**: `python tests/test_simulator.py`
- **Offline / Standalone**: Open `client/Simulator.html` directly in browser (`file://`).
- **Deploy to Railway**: Pre-configured via `railway.json`, `Dockerfile`, `Procfile`, and `nixpacks.toml`. Dynamic `$PORT` handling and healthchecks at `/api/health`.


