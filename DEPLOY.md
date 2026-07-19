# Deploying to a server

How to take Manero from your laptop to a real website, and how the database is
handled once it holds real orders.

---

## Read this first: three things to fix before taking real money

These are not deployment mechanics — they are gaps in the application that only
matter once real customers arrive.

### 1. The site tells customers you emailed them a receipt. It doesn't.

`OrderConfirmationView.vue` says *"Thanks — we've emailed the receipt to …"*, and
nothing in the codebase sends email. In development that was harmless. In
production it is a false statement to a paying customer, and it means **you have
no record of the sale reaching the buyer** — they can't forward a receipt, and
they'll email you asking where it is.

Fix before launch, either by:
- wiring up transactional email (Amazon SES, Resend, Postmark) and actually
  sending an order confirmation, or
- changing the wording to the truth: *"Your order is confirmed. Keep your order
  number for reference."*

### 2. There is no way to see or fulfil orders except by querying the database

There's no admin screen. To find out what to ship you'd run SQL by hand. Before
launch you need at least a way to list paid orders — even a read-only page or a
scheduled email of new orders. Phase 3 in the README covers a proper admin panel.

### 3. Stock can go negative under concurrent orders

Stock is checked, then decremented in a separate step. If two customers check out
for the last bag at the same moment, both can pass the check. It hasn't mattered
with one person testing; it will matter on a launch-day spike. The fix is a row
lock (`SELECT … FOR UPDATE`) or a conditional update at decrement time.

None of these block *deploying* — they block **selling**.

---

## What changes between your laptop and a server

| | Development (now) | Production |
| --- | --- | --- |
| Frontend | Vite dev server on `:5173` | Static files built by `npm run build`, served by a web server or CDN |
| API calls | Vite proxies `/api` → `:8000` | Real URL, e.g. `https://api.manero.in` |
| Database | Local instance on `:5433`, no password | Managed Postgres, strong password, TLS |
| Payments | `dummy` provider | `razorpay` with live keys |
| Secrets | `.env` file on disk | Injected by the host, never committed |
| HTTPS | none | required (payments and passwords) |

---

## Recommended setup

For a store this size, the lowest-effort path that still behaves properly:

- **Database:** a *managed* PostgreSQL service — DigitalOcean Managed Databases
  (Bangalore region), AWS RDS (Mumbai, `ap-south-1`), or Neon.
- **Backend:** a container or small VM in the same region as the database.
- **Frontend:** static hosting with a CDN — Cloudflare Pages, Netlify, Vercel, or
  an S3 bucket behind CloudFront.

Pick a region physically close to your customers. For India that means Mumbai or
Bangalore — using a US region adds roughly 200ms to every request.

**Why managed Postgres rather than installing it on the server yourself?** It's
around $15/month, and it gives you automated daily backups, point-in-time
recovery, TLS, and patching. Running your own means *you* are responsible for
backups — and the failure mode is discovering they were never configured on the
day you need them. For a database holding customer orders and addresses, that
trade is worth the money.

---

## Step by step

### 1. Create the database

In your provider's console, create a PostgreSQL 16 or 17 instance. Note the
connection details. Then create the app's user and database:

```sql
CREATE USER manero WITH PASSWORD '<a long random password>';
CREATE DATABASE manero OWNER manero;
```

Restrict network access to your backend server's IP — never leave a database open
to the whole internet.

### 2. Set the backend's environment variables

Set these on the host (not in a file you commit):

```
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://manero:<password>@<host>:5432/manero?ssl=require
SYNC_DATABASE_URL=postgresql+psycopg://manero:<password>@<host>:5432/manero?sslmode=require

CORS_ORIGINS=https://manero.in,https://www.manero.in

PAYMENT_PROVIDER=razorpay
RAZORPAY_KEY_ID=rzp_live_xxxxxxxx
RAZORPAY_KEY_SECRET=<live secret>

SHIPPING_FEE_PAISE=4900
FREE_SHIPPING_THRESHOLD_PAISE=59900
```

Two safeguards worth knowing:

- `ENVIRONMENT=production` makes the app **refuse to start with
  `PAYMENT_PROVIDER=dummy`**. A fake gateway in production would accept forged
  payments as real ones, so this is deliberately a hard failure, not a warning.
- `CORS_ORIGINS` must list your real domains. Leave it at `localhost` and the
  browser will block your own site from calling the API.

### 3. Run the migrations

On every deploy, before the new code starts serving:

```bash
alembic upgrade head
```

This is what creates and updates tables. It is safe to run repeatedly — already
applied migrations are skipped. **Do not** run `seed_products.py` in production
unless you actually want the placeholder catalog; it is development sample data.

### 4. Start the API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

`--host 0.0.0.0` (not the default `127.0.0.1`) so it accepts traffic from outside
the container. Put it behind nginx or your platform's load balancer, terminating
HTTPS there. Never expose port 8000 to the internet directly.

### 5. Build and deploy the frontend

```bash
cd frontend
npm ci
VITE_API_BASE_URL=https://api.manero.in npm run build
```

That produces `frontend/dist/` — plain static files. Upload them to your static
host.

**This step is easy to get wrong.** In development the Vite proxy forwards `/api`
to the backend; in a production build there is no proxy, so
`VITE_API_BASE_URL` must point at your real API. Miss it and the site loads fine
but every product list is empty, because it's calling a `/api` path that nothing
serves.

Also configure your host to serve `index.html` for unknown paths (SPA fallback).
Without it, refreshing on `/shop/instant-hazelnut` returns a 404 — the route
exists only in the browser.

### 6. Switch Razorpay to live mode

Live keys require KYC approval on your Razorpay account — start that early, it is
not instant. Test the whole flow with test keys on the deployed site *before*
switching, then make one small real purchase yourself and confirm the money
arrives and the order shows `paid`.

---

## Managing the database once it's live

### Backups

Turn on automated daily backups in your provider's console. Then — and this is
the part people skip — **restore one into a scratch database and confirm it
works**. An untested backup is a guess, not a safety net.

### Schema changes

Never edit tables by hand in production. Change the SQLAlchemy models locally,
generate a migration, test it against a copy of production data, then deploy:

```bash
alembic revision --autogenerate -m "add loyalty points"
alembic upgrade head
```

Autogenerate is a drafting aid, not an oracle — read the generated file before
applying it. It routinely misses renames (it will drop the old column and create
a new empty one, silently destroying the data) and column type changes.

### Access

The `manero` user only needs to read and write its own tables. Don't run the app
as a superuser, and keep a separate admin credential for maintenance.

### Data you're now responsible for

Orders contain names, addresses, phone numbers, and email addresses. Under India's
DPDP Act that carries obligations: keep it only as long as you need it, secure it
in transit and at rest, and be able to delete a customer's data on request. Card
details never touch your servers — Razorpay handles those — and it should stay
that way. Never log a full payment payload.

---

## Deployment checklist

- [ ] Managed Postgres created, network-restricted, backups enabled
- [ ] A backup actually restored and verified
- [ ] `ENVIRONMENT=production`
- [ ] `PAYMENT_PROVIDER=razorpay` with live keys
- [ ] `CORS_ORIGINS` set to real domains
- [ ] Secrets injected by the host, absent from git
- [ ] `alembic upgrade head` runs on deploy
- [ ] Frontend built with `VITE_API_BASE_URL`
- [ ] SPA fallback to `index.html` configured
- [ ] HTTPS everywhere, port 8000 not publicly exposed
- [ ] Order confirmation emails sending — or the false claim removed
- [ ] A way to view paid orders for fulfilment
- [ ] Stock decrement made concurrency-safe
- [ ] One real test purchase completed end to end

---

## Related

- Architecture, payments, first-time setup → [README.md](README.md)
- Changing products, prices, images → [EDITING.md](EDITING.md)
- Running locally → [START.md](START.md)
