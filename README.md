# Court Booking Revenue Simulator

An interactive unit economics, monetization model comparison, and multi-month projections simulator for court booking networks.

---

## Key Features

1. **Focused Three-Model Engine**:
   - **Model A: Commission (Turnover %)** — Percentage take on court gross turnover (with payment gateway fee deduction and customizable liaison split).
   - **Model B: Flat Subscription (₹/court/mo)** — Fixed monthly subscription fee per court with 0% platform fee deduction (gateway paid by court owner).
   - **Model C: Fixed Platform Booking Fee (₹/booking)** — Fixed flat platform fee per booking with 0% gateway fee deduction.
   - Dual currency support: **INR (₹)** and **AED (AED)**.

2. **Tab 1: Month 1 Snapshot & Unit Economics (Complete Parameter Transparency)**:
   - **Parameter Controls**: Interactive sliders and inputs for pipeline capacity, court density, liaison network, and monetization levers.
   - **Calculation Anatomy Card**: Step-by-step mathematical walkthrough showing how selected parameters derive the exact Month 1 figures:
     - *Step 1: Network Footprint* (Venues × Courts/Venue = Courts/Liaison × Liaisons = Total Network Courts).
     - *Step 2: Utilization* (Hours/wk × 4 wks = Monthly Hours/Bookings).
     - *Step 3: Unit Net / Court* (Formulas for Gross GMV, Net Commission, Flat Fees).
     - *Step 4: Realization & Split* (Liaison Payout vs Company Revenue).
   - **Month 1 Model Comparison Matrix**: Select any two models (e.g., Model B vs Model A) to compare Unit Net, 1 Liaison Payout, Total Company Revenue, Surplus Delta, and Break-Even utilization.

3. **Tab 2: Projections & Horizon Simulator (Month X to Month Y)**:
   - **Customizable Horizon Window**: Quick presets (3, 6, 12, 24 months) or custom **From Month X to Month Y** range inputs.
   - **Horizon Milestones**: Ending network footprint, cumulative period revenue for each model, ending run-rates, and net surplus.
   - **Trajectory Line Chart**: Responsive Chart.js graph comparing Model A, B, and C with view modes for Company Revenue, 1 Liaison Take-Home, or Combined series.
   - **Multi-Month Ledger**: Dynamic month-by-month table filtered to the selected horizon with totals summary footer.

4. **Tamper-Proof Server-Side Google OAuth 2.0 Authentication**:
   - Protected behind Python 3 server (`server.py`) using standard library (zero external pip packages required).
   - Google ID tokens cryptographically verified using Google's public endpoints.
   - Strict server-side whitelist (`ALLOWED_USERS`).
   - Unauthorized accounts **never receive the HTML/JS simulator code** (rejected with HTTP 403 / redirected to `/login`).
   - Issues HMAC-SHA256 signed `HttpOnly`, `SameSite=Lax` session cookies.
   - Includes Developer Mode toggle for local testing.

---

## Quick Start (Running with Python 3)

### 1. Launch the Server

In your shell (e.g. zsh, bash, or terminal):

```bash
python3 server/server.py
```

The server will start on `http://localhost:8000/`.

### 2. Configure Environment (`.env`)

Edit `.env` to configure your Google OAuth Client ID and authorized user emails:

```bash
# 1. Google OAuth Client ID (from Google Cloud Console)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com

# 2. Server-side Allowed Emails (Comma-separated)
ALLOWED_USERS=admin@example.com,founder@yourdomain.com,karthik@example.com

# 3. Optional Allowed Domains
ALLOWED_DOMAINS=yourcompany.com

# 4. Session Secret
SESSION_SECRET=your-secure-random-secret-key-12345

# 5. Port
PORT=8000

# 6. Developer Mode (Set to false in production)
DEV_MODE=true
```

### 3. Accessing the Application

- Visit `http://localhost:8000/`.
- If not signed in, you are redirected to `/login`.
- Sign in with an approved Google account:
  - If your email is on the whitelist, you are granted access and redirected to the simulator.
  - If your email is not on the whitelist, access is denied (HTTP 403).
- In Developer Mode (`DEV_MODE=true`), you can test the login flows directly with the "Test as Authorized User" and "Test Unauthorized User" buttons.

### 4. Server Configuration (`config/config.json`)

Starting parameters, rates, fees, splits, and slider bounds for **INR** and **AED** are configured centrally in `config/config.json` and served via `/api/config`:
- **Separate Pipelines**: Independent footprint settings (`courtsPerVenue`, `startingVenues`, `venueGrowth`, `liaisonCount`) for each currency.
- **Model Levers & Bounds**: Configurable base rate, subscription fee, booking fee, min/max/step ranges, and revenue splits.
- Changes made in `config/config.json` take effect immediately on page refresh without needing code modifications in HTML.

### 5. Deploying to Railway

The repository is pre-configured with `railway.json`, `Dockerfile`, `Procfile`, and `nixpacks.toml` for seamless deployment to [Railway](https://railway.app):

1. **Connect Repo**: In Railway, create a **New Project** and select **Deploy from GitHub repo**.
2. **Environment Variables**: Add your production variables in the Railway dashboard:
   - `SESSION_SECRET`: A secure random cryptographic secret.
   - `ALLOWED_USERS`: Comma-separated list of authorized Google emails (e.g. `karthik@example.com`).
   - `ALLOWED_DOMAINS` *(optional)*: Permitted domain(s) (e.g. `yourcompany.com`).
   - `GOOGLE_CLIENT_ID`: Your Google OAuth 2.0 Web Client ID.
   - `DEV_MODE`: Set to `false` for production.
3. **Health Check**: Railway automatically monitors `/api/health` with automatic restart policies.

### 6. Automated Verification & Testing

Run the zero-dependency test suite to verify configuration integrity, DOM bindings, session cryptographic signing, and deployment configs:

```bash
python tests/test_simulator.py
```

### 7. AI Agent Guidelines & Synchronization

This repository includes specialized instructions for all major AI coding agents:
- Universal: `AGENTS.md`
- Google Antigravity & Gemini: `GEMINI.md` and `.agents/rules/simulator-invariants.md`
- Anthropic Claude Code: `CLAUDE.md`
- Cursor IDE: `.cursorrules`
- GitHub Copilot: `.github/copilot-instructions.md`

**Synchronization Requirement**: Whenever changes are made to this codebase (features, routes, calculation logic, DOM IDs, configuration keys, or styles), the modifying agent must synchronously update all agent instruction files and `tests/test_simulator.py` to maintain repository alignment.




