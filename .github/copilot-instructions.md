# GitHub Copilot Instructions — Court Booking Revenue Simulator

This repository contains the Court Booking Revenue Simulator.

## Architecture
- Single-page application in `client/Simulator.html` (vanilla HTML/JS + Tailwind CSS CDN + Chart.js CDN).
- Lightweight Python gatekeeper server in `server/server.py` using Python 3 standard library only.
- Configuration for INR and AED parameters and slider ranges in `config/config.json`.
- Authentication via Google OAuth (GIS) and dev mode in `client/login.html`.
- Automated verification tests in `tests/test_simulator.py`.


## Mandatory Guidelines
1. Do not introduce any external Python libraries (no `pip install`, no `requests`, no `flask`, no `requirements.txt`).
2. Do not introduce node/npm build chains (no `package.json`, no `webpack`, no `vite`).
3. For inputs that can accept zero (`0`), do not use falsy fallback (`parseInt(val) || default`); use `isNaN(val) ? default : val`.
4. Ensure currency formatting preserves trailing space for AED (`AED 15`) and no space for INR (`₹300`).
5. Ensure input currency badges use flexbox wrappers (`.input-prefix`) to prevent symbol/text overlap.
6. Refer to `AGENTS.md` for complete formulas, anatomy steps, and model comparison calculations.
7. **Mandatory Documentation Synchronization**: Whenever proposing or implementing changes that affect architecture, calculation formulas, DOM IDs, configuration keys, or server endpoints, you MUST update all agent instruction files (`AGENTS.md`, `GEMINI.md`, `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`, `.agents/rules/simulator-invariants.md`, and `README.md`) and verify against `test_simulator.py`. Outdated documentation is a breaking defect.

