# AGENTS.md — Court Booking Revenue Simulator

This document provides essential context, architecture details, and operational rules for any AI agent working on this repository.

---

## 1. Project Overview

The **Court Booking Revenue Simulator** is a full-stack, single-page application and lightweight Python server designed to model, compare, and forecast revenue across court booking networks.

It allows stakeholders to compare three distinct monetization architectures:
- **Model A: Commission (Turnover %)** — Percentage fee on gross court turnover minus payment gateway deductions.
- **Model B: Flat Subscription (₹ or AED/court/mo)** — Fixed monthly platform subscription per court (0% fee deduction; gateway paid by venue).
- **Model C: Fixed Platform Booking Fee (₹ or AED/booking)** — Fixed flat fee per booking slot (0% fee deduction; gateway paid by venue).

Dual currency support: **INR (₹)** and **AED (AED)**.

---

## 2. Repository File Map

```
simulator/
├── client/                     # Frontend UI & client applications
│   ├── Simulator.html          # Core interactive simulator application
│   ├── index.html              # Mirror/symlink of Simulator.html
│   └── login.html              # Google OAuth & Dev Mode login portal
├── server/                     # Backend server logic & gatekeeper
│   ├── __init__.py             # Python server package init
│   └── server.py               # Zero-dependency Python 3 HTTP server & gatekeeper
├── config/                     # Configuration definitions
│   └── config.json             # Central configuration for currency parameters & bounds
├── tests/                      # Automated test suites
│   └── test_simulator.py       # Automated verification test suite
├── .agents/                    # Workspace rules & customizations
│   └── rules/                  # Antigravity workspace rules (simulator-invariants.md)
├── .github/                    # GitHub & Copilot workspace instructions
│   └── copilot-instructions.md # GitHub Copilot workspace instructions
├── .cursorrules                # Cursor IDE AI coding rules & invariants
├── .env                        # Local environment configuration (ports, secrets, whitelists)
├── .env.example                # Example template for environment variables
├── .gitignore                  # Git ignore rules (protects .env and cache)
├── Dockerfile                  # Self-contained container definition for Railway/Docker
├── .dockerignore               # Protects secrets (.env) and cache from container image
├── railway.json                # Railway deployment configuration (healthcheck, builder)
├── Procfile                    # Web process command definition
├── nixpacks.toml               # Nixpacks build configuration for Railway
├── requirements.txt            # Zero-dependency standard library indicator
├── runtime.txt                 # Python 3.12 runtime indicator
├── AGENTS.md                   # Universal AI agent guide & development rules
├── GEMINI.md                   # Antigravity / Gemini root workspace instructions
├── CLAUDE.md                   # Claude Code onboarding guide & quick commands
└── README.md                   # Human-facing project overview & quick start
```

### Key Responsibilities

| Path | Purpose | Tech Stack |
| :--- | :--- | :--- |
| `server/server.py` | Server gatekeeper, session issuer, Google OAuth token verifier, static file server, and `/api/config` provider. | Python 3 Standard Library only (zero external pip packages). |
| `client/Simulator.html` | Core UI, interactive parameter controls, mathematical calculation engine, Chart.js visualizer, multi-month ledger. | Vanilla HTML5, Vanilla JavaScript, Tailwind CSS (CDN), Chart.js (CDN). |
| `client/login.html` | Sign-in interface supporting Google Identity Services (GIS) and local Dev Mode one-click login. | Vanilla HTML/JS, Tailwind CSS (CDN). |
| `config/config.json` | Central configuration file defining starting pipeline parameters, model levers, and slider ranges for INR and AED. | JSON. |
| `tests/test_simulator.py` | Automated verification test suite for config schema, DOM ID bindings, zero-dependency rules, session crypto, and Railway deploy config. | Python 3 standard library (`unittest`). |
| `railway.json` / `Dockerfile` | Railway production deployment configuration, containerization, and health check definitions. | Docker / Nixpacks. |

---

## 3. How to Run Locally & Test

### Prerequisites
- Python 3.8+ installed (Windows: `python`, Unix/macOS: `python3`).
- **No package manager / npm / pip install required**.

### Launching the Server
```bash
python server/server.py
# or on macOS / Linux:
python3 server/server.py
```
Default URL: `http://localhost:8000/`

### Running the Test Suite
```bash
python tests/test_simulator.py
# or with unittest:
python -m unittest tests/test_simulator.py
```
This tests in < 1 second:
- Absence of unauthorized third-party Python imports.
- Schema integrity of `config.json`.
- Synchronization of DOM element IDs between `Simulator.html` and `config.json`.
- Input group flex styling and zero-falsy bug prevention.
- Cryptographic session token generation and verification.

### Development Mode (Testing without Google OAuth)
In `.env`:
```env
DEV_MODE=true
PORT=8000
ALLOWED_USERS=admin@example.com,developer@example.com
```
When `DEV_MODE=true`:
1. Navigating to `http://localhost:8000/` unauthenticated redirects to `/login`.
2. On `/login`, click **"Test as Authorized User"** to immediately sign in as `developer@example.com` without needing real Google credentials.

### Standalone Mode (Offline / Without Python)
`Simulator.html` can also be opened directly via `file:///.../Simulator.html` in a web browser.
Built-in graceful fallbacks in `Simulator.html`:
- If `/api/config` fails, it falls back to built-in default configuration.
- If `/api/me` fails, it activates a "Standalone Mode" badge and bypasses auth.

### Deploying to Railway
The repository is fully pre-configured for one-click deployment to [Railway](https://railway.app):
- **Build Configurations**: Includes both `railway.json` + `Dockerfile` (primary) and `Procfile` + `nixpacks.toml` (Nixpacks fallback).
- **Zero Configuration Port Binding**: `server.py` dynamically binds to `0.0.0.0:$PORT` provided by Railway.
- **Healthcheck**: Configured to monitor `/api/health` with automatic failure restarts.
- **Environment Variables**: Configure the following in Railway's Service Variables:
  - `SESSION_SECRET`: A long random secret string.
  - `ALLOWED_USERS`: Comma-separated list of authorized Google emails.
  - `ALLOWED_DOMAINS` *(optional)*: Permitted email domains (e.g. `yourcompany.com`).
  - `GOOGLE_CLIENT_ID`: Your Google OAuth 2.0 Web Client ID.
  - `DEV_MODE`: Set to `false` for production.

---

## 4. Architecture & Key Workflows

### 4.1. Authentication & Gatekeeper Flow
- **Protected Routes**: `/`, `/index.html`, `/Simulator.html` require a valid signed session cookie (`sim_session`).
- **Access Control**:
  - `server.py` checks `verify_session_token(token)`.
  - Tokens are signed with HMAC-SHA256 using `SESSION_SECRET`.
  - The token payload contains user email and expiration timestamp (default: 7 days).
  - Unauthenticated requests receive HTTP 302 redirect to `/login`.
  - **Unauthorized emails NEVER receive `Simulator.html` source code**.
- **Whitelisting**:
  - Controlled via `ALLOWED_USERS` (comma-separated emails) and `ALLOWED_DOMAINS` in `.env`.
  - Verified on every request; revoking an email in `.env` revokes access immediately.

### 4.2. Configuration System (`config.json`)
Starting parameters and range bounds are defined in `config.json`:
- Exposed via `GET /api/config` in `server.py`.
- On startup, `Simulator.html` calls `loadServerConfig()` to load parameters.
- Changing `config.json` updates defaults across both client and server upon page refresh without touching code.
- Supported currency sections:
  - `pipeline`: `courtsPerVenue`, `startingVenues`, `venueGrowth`, `liaisonCount`.
  - `modelA`: `baseRate`, `baseRateMin`, `baseRateMax`, `baseRateStep`, `hoursPerWeek`, `grossCommission`, `gatewayFee`, `licenseeShare`.
  - `modelB`: `subscriptionCost`, `subscriptionMin`, `subscriptionMax`, `rangeStep`, `inputStep`, `licenseeShare`.
  - `modelC`: `bookingFee`, `bookingFeeMin`, `bookingFeeMax`, `bookingFeeStep`, `licenseeShare`.
  - `syncSplit`: Boolean (sync licensee percentage across models).
  - `horizon`: Window start and end months.

### 4.3. Client Simulation Engine (`Simulator.html`)
The frontend is driven by `calculate()`:
1. **Reads Inputs**: Safely extracts user values using `isNaN(...)` checks.
2. **Unit Economics**:
   - `monthlyHoursPerCourt = hoursPerWeek * 4`
   - `gmvPerCourtMonth = baseRate * monthlyHoursPerCourt`
   - `modelANetPerCourt = gmvPerCourtMonth * ((grossCommission - 2) / 100)`
   - `modelBNetPerCourt = subscriptionCostPerCourt`
   - `modelCNetPerCourt = bookingFee * monthlyHoursPerCourt`
3. **Month 1 Footprint & Earnings**:
   - `m1CourtsPerLiaison = startingVenues * courtsPerVenue`
   - `m1TotalNetworkCourts = m1CourtsPerLiaison * liaisonCount`
   - Computes 1 Liaison Take-Home and Company Revenue based on licensee split %.
4. **Step-by-Step Anatomy Card**:
   - Dynamically walks through Footprint (Step 1), Utilization (Step 2), Unit Net (Step 3), and Realization (Step 4).
5. **Comparison Matrix & Break-Even Occupancy**:
   - Dynamically calculates occupancy break-even: `breakEvenHrsPerWeek = subscriptionCost / (baseRate * 4 * netCommissionRate)`.
6. **Multi-Month Horizon & Chart Engine**:
   - Projects 36 months forward based on `venueGrowth`.
   - Slices projection window between `horizonStart` and `horizonEnd`.
   - Populates Chart.js line graph and period ledger table.

---

## 5. Strict Coding Rules & Invariants

When modifying or extending this codebase, adhere strictly to these constraints:

### Rule 1: Zero External Python Dependencies
- **NEVER** add `pip install`, `requirements.txt`, or third-party dependencies (such as Flask, FastAPI, Requests, PyJWT) to `server.py`.
- `server.py` **must remain runnable with a bare-bones Python 3 installation**. Use only built-in standard modules (`http.server`, `urllib`, `json`, `hmac`, `hashlib`, `base64`, `time`, `os`).

### Rule 2: No Frontend Build Step
- Do not add `package.json`, Vite, Webpack, Babel, or NPM tooling.
- All styles use **Tailwind CSS via CDN** (`<script src="https://cdn.tailwindcss.com"></script>`).
- Charts use **Chart.js via CDN** (`<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>`).

### Rule 3: Input Zero-Falsy Protection & DRY Schema
- In `calculate()` and state handling, never use `parseInt(val) || default` for inputs where `0` is a valid entry (e.g. `startingVenues`, `venueGrowth`).
- All simulation inputs are registered in the unified `SIM_PARAMS` schema and safely read via `getSafeParam(param)`, which guarantees zero-falsy bug prevention across both integer and float inputs.

### Rule 4: Companion Input & Share Synchronization
- Whenever a slider has a companion numeric input (e.g. `subCost` range slider and `subCostInput` number field), ensure both are synced:
  - Moving the slider calls `syncSubCostInput(this.value); calculate()`.
  - Typing in the input calls `syncSubCostRange(this.value); calculate()`.
  - In `calculate()`, explicitly set `setVal('subCostInput', subCost)`.
- Licensee share sliders across models are kept in sync DRYly via `syncShare(sourceId)`.


### Rule 5: Currency Symbol Alignment & Spacing
- **INR (`₹`)**: Displayed without trailing space (`₹300`).
- **AED (`AED `)**: Must include trailing space in text labels (`AED 15`, `AED 200`).
- **Input Prefix Badges**: Currency symbols embedded inside input boxes must use the **Flexbox Input Group pattern** with `.input-prefix`:
  ```html
  <div class="flex items-center rounded-lg border border-slate-200 bg-white focus-within:ring-2 ...">
      <span class="currency-symbol input-prefix pl-3 pr-1 text-xs ...">₹</span>
      <input type="number" id="baseRate" class="w-full pr-3 py-1.5 bg-transparent border-0 focus:outline-none focus:ring-0" ...>
  </div>
  ```
  *Never use absolute positioning over inputs* — multi-character symbols (`AED`) will overlap with input text.

### Rule 6: Mandatory Agent & Documentation Synchronization
- **CRITICAL**: Whenever ANY modifications are made to this repository (including changes to architecture, calculation formulas, input elements, DOM IDs, configuration keys in `config.json`, endpoints in `server.py`, or UI layouts):
  1. **YOU MUST UPDATE ALL AGENT INSTRUCTION FILES IN TANDEM**:
     - `AGENTS.md` (this file — universal reference)
     - `GEMINI.md` (Antigravity & Gemini instructions)
     - `CLAUDE.md` (Claude Code instructions)
     - `.cursorrules` (Cursor IDE rules)
     - `.github/copilot-instructions.md` (GitHub Copilot instructions)
     - `.agents/rules/simulator-invariants.md` (Antigravity workspace rules)
     - `README.md` (Human documentation)
     - `test_simulator.py` (Verification test suite — ensure tests cover any new inputs, routes, or constraints)
  2. **Never leave documentation or agent rules in a stale state**. Outdated documentation or desynchronized instructions will mislead subsequent agents and are considered breaking defects.

---

## 6. Verification & Quality Checklist

Before finalizing ANY changes, verify:
1. **Server Health**:
   - `GET /api/health` returns `{"status": "healthy"}`.
   - `GET /api/config` returns valid JSON matching `config.json`.
2. **Auth Verification**:
   - Visiting `/` when logged out redirects to `/login`.
   - In dev mode, clicking "Test as Authorized User" grants access and redirects to `/`.
3. **Currency Switch Test**:
   - Toggling from **INR** to **AED** updates symbols, labels, and starting parameters smoothly.
   - Currency prefixes do not overlap numeric text inside input fields.
   - Toggling back to **INR** restores INR state accurately.
4. **Calculations**:
   - Verify that modifying sliders immediately updates KPI cards, Anatomy cards, Comparison matrix, Chart, and Ledger table without console errors.
5. **Agent & Docs Sync Verification**:
   - Confirm that all agent instruction files (`AGENTS.md`, `GEMINI.md`, `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`, `.agents/rules/simulator-invariants.md`, and `README.md`) accurately reflect the current state of the codebase.
   - Confirm that `python test_simulator.py` passes.
