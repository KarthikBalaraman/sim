# CLAUDE.md — Claude Code Guidelines

## Overview
Court Booking Revenue Simulator — A dual-currency (INR & AED) unit economics and revenue model comparison tool with a Python 3 gatekeeper server.

## Commands
- **Start Server**: `python server/server.py` (serves on `http://localhost:8000/`)
- **Run Tests**: `python tests/test_simulator.py`
- **Standalone**: Open `client/Simulator.html` directly in any web browser.

## Architecture
- `server/server.py`: Standard-library HTTP server handling session tokens, Google OAuth 2.0 verification, email whitelisting, and `/api/config`.
- `client/Simulator.html`: Client-side single-page app containing unit economics formulas, Chart.js visualizer, and 36-month projection ledger.
- `client/login.html`: Login page supporting Google GIS and Dev Mode one-click login.
- `config/config.json`: Centralized parameter definitions and slider bounds for INR and AED.
- `railway.json`, `Dockerfile`, `Procfile`, `nixpacks.toml`: Pre-configured Railway / Docker deployment specifications.
- `tests/test_simulator.py`: Zero-dependency automated test suite.
- `AGENTS.md`: Full architectural reference document.

## Critical Invariants
- **Python**: Standard library ONLY (`http.server`, `urllib`, `hmac`, `hashlib`, `json`, etc.). Never add pip dependencies.
- **Frontend**: Zero-build. Tailwind CSS and Chart.js via CDN. Never add `package.json` or build tools.
- **Currency formatting**: INR uses `₹` with no space; AED uses `'AED '` with trailing space in labels. Inside inputs, use `.input-prefix` flexbox containers.
- **Zero-falsy bug prevention**: Always use `isNaN()` checks or `getSafeParam()` when reading input values.
- **Config-driven**: When updating default parameters or bounds, update `config/config.json`.
- **Session & Signout Invariant**: Clear cookies with matching transport attributes (`SameSite=None; Secure` on HTTPS, `SameSite=Lax` on HTTP, `Max-Age=0`, `Expires=Thu, 01 Jan 1970 00:00:00 GMT`), redirect to `/login?logged_out=1` with `Cache-Control: no-cache, no-store, must-revalidate`, and invoke `google.accounts.id.disableAutoSelect()`.
- **Mandatory Documentation & Agent Sync**: Whenever making ANY changes to routes, math, inputs, config keys, or styles, you MUST update all agent instruction files (`AGENTS.md`, `GEMINI.md`, `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`, `.agents/rules/simulator-invariants.md`, and `README.md`) and verify with `test_simulator.py`. Outdated documentation is considered a breaking defect.


