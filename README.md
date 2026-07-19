# Manero

Online store for Manero coffee — browse the catalog, filter by bean/roast/grind/flavour,
add to cart, and check out with Razorpay. Guest checkout; no account required to buy.

- **Frontend** — Vue 3 + TypeScript + Vite (`frontend/`)
- **Backend** — FastAPI + SQLAlchemy 2.0 + Alembic, PostgreSQL (`backend/`)
- **Payments** — pluggable. Ships with a dummy gateway so checkout works out of
  the box; Razorpay is a one-line config change.

---

## Prerequisites

| Tool | Version | Notes |
| --- | --- | --- |
| Node.js | 20+ | For the frontend |
| Python | 3.12+ | For the backend (3.12+ required — the code uses `StrEnum` and `datetime.UTC`) |
| PostgreSQL | 16+ | Either a local install or via Docker. Verified on 17. |
| Docker | optional | Only needed if you want Postgres via `docker-compose` |

**Looking for how to change products, prices, images, or colours?** See
[EDITING.md](EDITING.md) — it covers the everyday edits without the architecture.

---

## Setup

### 1. Database

> **How this machine is currently set up.** There is a PostgreSQL 17 service on the
> default port **5432** that predates this project, and whose `postgres` password isn't
> recorded anywhere. Rather than change that server's credentials or its auth config,
> the project runs its **own** PostgreSQL instance on port **5433**, with its data in
> `.pgdata/` at the repo root (gitignored). The two are completely independent — nothing
> the project does can affect the 5432 server or its databases.
>
> That's why `backend/.env` points at port **5433**, not 5432.
>
> **Starting it** (after a reboot, or if connections are refused):
>
> ```powershell
> & "C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe" -D "C:\Manero-Project\manero\.pgdata" -o "-p 5433" -l "C:\Manero-Project\manero\.pgdata\server.log" start
> ```
>
> **Stopping it:**
>
> ```powershell
> & "C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe" -D "C:\Manero-Project\manero\.pgdata" stop
> ```
>
> Unlike the 5432 service, this instance does **not** start automatically on boot.
>
> Local connections to it use `trust` auth (no password) because it listens only on
> localhost and holds nothing but this project's development data. If you ever expose it
> beyond localhost, change that first — see `.pgdata/pg_hba.conf`.
>
> To switch to the 5432 server instead, create the role and database there and change the
> port back to 5432 in `backend/.env`.

Starting from scratch on another machine, either option below works.

With Docker:

```bash
docker compose up -d db
```

Without Docker, install PostgreSQL and create the project's user and database. Run this
as the `postgres` superuser (you'll be prompted for its password):

```
psql -U postgres -h localhost -c "CREATE USER manero WITH PASSWORD 'manero';"
psql -U postgres -h localhost -c "CREATE DATABASE manero OWNER manero;"
```

On Windows, `psql` is at `C:\Program Files\PostgreSQL\17\bin\psql.exe` and isn't on PATH
by default — either use the full path or add that `bin` folder to PATH.

### If Postgres isn't running

Check first:

```
& "C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe" -D "C:\Program Files\PostgreSQL\17\data" status
```

Normally PostgreSQL runs as a Windows service that starts on boot. If the service is
missing (a botched upgrade can drop its registration), you can start the server manually:

```
& "C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe" -D "C:\Program Files\PostgreSQL\17\data" start
```

Starting it that way runs the server as your own user; it works, but the service is the
normal route. To start the service (Administrator terminal required):

```
Start-Service postgresql-x64-17
```

The service is set to `Automatic`, so it starts on boot without any of this.

### 2. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
cp .env.example .env          # then edit .env

alembic upgrade head          # create the tables
python -m app.seeds.seed_products   # load ~12 placeholder products

uvicorn app.main:app --reload --port 8000
```

API docs: <http://localhost:8000/docs> · Health: <http://localhost:8000/health>

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Storefront: <http://localhost:5173>

The Vite dev server proxies `/api` to `http://localhost:8000`, so the frontend and API
are same-origin in development and CORS never comes up.

---

## Payments

The store talks to a `PaymentProvider`, never to a gateway directly
(`backend/app/services/payments.py`). Which one is live is set by one line in
`backend/.env`:

```
PAYMENT_PROVIDER=dummy      # or: razorpay
```

### `dummy` (the default)

No account, no keys, no network. Checkout opens an in-app dialog offering
**Simulate successful payment** / **Simulate failed payment** / **Cancel**, and the
rest of the flow proceeds exactly as it would with a real gateway.

It is not a stub that skips verification: the dummy provider signs its callbacks with
HMAC-SHA256, the same scheme Razorpay uses, and the server verifies that signature on
the normal `/checkout/verify` path. The failure button returns a deliberately invalid
signature so you can see the rejection path work. Signing happens server-side —
`/checkout/dummy-pay` mints the payload — so no secret ever reaches the browser.

**It refuses to start when `ENVIRONMENT=production`.** A fake gateway in production
would wave forged payments through as real ones.

### Switching to Razorpay

Set `PAYMENT_PROVIDER=razorpay` and add keys from the
[Razorpay dashboard](https://dashboard.razorpay.com/app/keys) with **Test Mode** on:

```
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
```

That's the whole change — no code edits. `/checkout/dummy-pay` starts returning 404 the
moment a real provider is active, and the frontend opens Razorpay Checkout instead of
the simulation dialog.

`RAZORPAY_KEY_ID` is public and gets sent to the browser. **`RAZORPAY_KEY_SECRET` must
never leave the server** — it is what signs and verifies payments.

Test card: `4111 1111 1111 1111`, any future expiry, any CVV.

### How payment is secured

1. The browser posts the cart token and shipping address — **not** a price.
2. The server recomputes the total from the `product_variants` rows and creates the
   gateway order for that amount. Nothing the client sends about money is trusted.
3. The gateway returns a signature. The server verifies it with HMAC-SHA256 before
   marking the order paid.

An order only becomes `paid` after that server-side signature check passes. This holds
for both providers.

---

## Tests

```bash
cd backend
pytest
```

The suite runs against in-memory SQLite using the dummy payment provider, so it needs
neither Postgres nor network access. It covers filtering, cart maths, and the checkout
guarantees above — that a client-supplied price is ignored, that a tampered signature is
rejected, that a repeated payment callback doesn't decrement stock twice, and that the
dummy provider is refused in production.

---

## Branding

Gold-on-black, taken from the Manero mark. The header, footer and hero sit on near-black
(`--espresso`) because gold only reads as gold against a dark ground.

### The logo

`frontend/src/assets/logo/` holds two files:

| File | Role |
| --- | --- |
| `manero-logo.jpeg` | The original artwork, untouched. Kept as the source to re-derive from. |
| `manero-logo.jpg` | What the site actually displays. |

The displayed version is the original with two changes:

1. **Cropped to content.** The original is square with ~20% black margin on every side,
   which would shrink the mark to a fraction of the header height.
2. **Background flattened to `#0d0b09`.** The original's ground is a soft dark-grey
   gradient, not flat black — against the header it showed as a visible lighter
   rectangle. Pixels below a luminance threshold are ramped to the page colour, so the
   gold's glow still feathers out instead of hard-clipping.

**To replace the logo:** overwrite `manero-logo.jpg`, keeping the name. No code change —
the header and footer both read from `index.ts`, which imports that one file.

Two consequences of using JPEG rather than SVG or PNG, worth knowing before you swap
files:

- **No transparency.** The dark ground is baked into the image, which is why the header
  and footer must stay `--espresso` (`#0d0b09`). Against any other colour a rectangle
  reappears. If you later want the logo on a light background, you need a PNG with an
  alpha channel — JPEG cannot do it.
- **Fixed resolution.** 1041px wide is comfortable for every current use (largest is
  ~92px tall in the footer), but it will not scale indefinitely the way a vector would.

The header is `84px` tall — deliberately generous, because the mark is a *stacked*
lockup (monogram above wordmark) and the wordmark turns to mush in a shorter bar.

### Colours

The palette is a block of CSS custom properties at the top of `frontend/src/style.css`.
Changing those values rebrands the whole storefront — but `--espresso` is coupled to the
logo's baked-in background, so changing it means re-flattening the logo to match.

## Product data

`backend/app/seeds/seed_products.py` holds ~12 placeholder coffees with realistic
attributes and Unsplash imagery. It matches on slug and updates in place, so re-running
it won't duplicate rows. Replace the `PRODUCTS` list with real SKUs when they exist.

---

## Layout

```
backend/
  app/
    api/v1/          products, cart, checkout endpoints
    core/            config, database, money helpers
    models/          SQLAlchemy models
    schemas/         Pydantic request/response models
    services/        pricing (single source of truth for totals),
                     payments (provider abstraction: dummy / razorpay)
    seeds/           catalog seed script
  alembic/           migrations
  tests/
frontend/
  src/
    api/             typed client + types mirroring the backend schemas
    components/      header, footer, product card, filters, cart drawer
    stores/          Pinia: cart, catalog
    views/           home, shop, product, cart, checkout, confirmation, 404
```

**Money is stored and computed as integer paise everywhere — never floats.** Formatting
to rupees happens only at the display edge (`formatInr`).

---

## Not built yet

- User accounts (`orders.user_id` is intentionally absent but the schema won't fight it —
  guest orders stay valid when it's added)
- Admin panel for managing products and orders
- Shipping-rate calculation (currently a flat ₹49, free over ₹599)
- Coupons, reviews, email receipts
