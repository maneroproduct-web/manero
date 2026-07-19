# How to start the application

Three things need to be running: **database → backend → frontend**, in that order.

## Quick way

```bash
./start.sh        # Git Bash, Linux, macOS
./stop.sh
```
```powershell
.\start.ps1       # PowerShell
.\stop.ps1
```

`start.sh` works on all three platforms and adapts to each:

| | What it does |
| --- | --- |
| **Windows** (Git Bash) | Hands off to `start.ps1`, which opens a window per service. Stop with Ctrl+C in those windows, then `./stop.sh` for the database. |
| **Linux / macOS** | Runs the services in the background, logging to `logs/` and recording PIDs. `./stop.sh` shuts everything down. |

> **Why is there a `.ps1` as well?** `.ps1` scripts only run in PowerShell. Running
> `./start.ps1` directly in Git Bash gives `line 10: =: command not found` and
> `syntax error near unexpected token '{'` — bash is trying to read PowerShell as a
> shell script. Use `./start.sh` in Bash and `.\start.ps1` in PowerShell.

### First run on Linux or macOS

`start.sh` bootstraps whatever is missing: it creates the PostgreSQL cluster in
`.pgdata/`, creates the `manero` user and database, and runs migrations. You need
PostgreSQL's tools on your PATH first:

```bash
# Debian / Ubuntu
sudo apt install postgresql
export PATH="/usr/lib/postgresql/17/bin:$PATH"   # not on PATH by default

# macOS
brew install postgresql@17
```

And the project's own dependencies, once:

```bash
cd backend  && python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt
cd ../frontend && npm install
```

It does **not** seed the catalog — run that yourself if you want the sample products:

```bash
cd backend && .venv/bin/python -m app.seeds.seed_products
```

The manual steps below are what these scripts do, in case you want to run them
yourself or something goes wrong.

---

## Step 1 — Start the database

Open PowerShell and run:

```powershell
& "C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe" -D "C:\Manero-Project\manero\.pgdata" -o "-p 5433" -l "C:\Manero-Project\manero\.pgdata\server.log" start
```

You should see `server started`. If it says **"another server might be running"**, it's
already up — carry on to step 2.

> **Why port 5433?** This project runs its own PostgreSQL instance, separate from the
> one already on your machine at port 5432. See the Database section of `README.md`.
> Unlike that one, this instance does **not** start automatically when you boot — which
> is why this step exists.

**Check it worked:**

```powershell
& "C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe" -D "C:\Manero-Project\manero\.pgdata" status
```

---

## Step 2 — Start the backend (API)

Open a **new** PowerShell window — this one stays running.

```powershell
cd C:\Manero-Project\manero\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Wait for:

```
Application startup complete.
Uvicorn running on http://127.0.0.1:8000
```

**Leave this window open.** Closing it stops the API.

**Check it worked:** open <http://localhost:8000/health> — you should see
`{"status":"ok", ...}`.

---

## Step 3 — Start the frontend (website)

Open a **third** PowerShell window.

```powershell
cd C:\Manero-Project\manero\frontend
npm run dev
```

Wait for:

```
➜  Local:   http://localhost:5173/
```

**Leave this window open too.**

---

## Step 4 — Open the site

<http://localhost:5173>

That's it. You now have three windows running: database (background), API, and website.

| What | Address |
| --- | --- |
| The shop | <http://localhost:5173> |
| API documentation | <http://localhost:8000/docs> |
| API health check | <http://localhost:8000/health> |

---

## How to stop everything

Press **Ctrl+C** in the backend and frontend windows, then stop the database:

```bash
./stop.sh          # Git Bash
```
```powershell
.\stop.ps1         # PowerShell
```

Leaving the database running is harmless if you'd rather not bother.

---

## If something goes wrong

**"connection refused" / the shop shows no products**
The database or the API isn't running. Redo steps 1 and 2. Products come from the
database via the API — if either is down, the shop loads but the shelves are empty.

**"Port 5173 is already in use"**
The frontend is already running in another window. Either use that one, or close it.
The site is deliberately configured to fail here rather than quietly move to port 5174,
which would leave <http://localhost:5173> pointing at nothing.

**"port 8000 is already in use"**
Same for the backend. Find the old window and Ctrl+C it, or:
```powershell
Get-Process -Name python | Stop-Process
```

**Backend won't start — `ModuleNotFoundError`**
The virtual environment is missing or incomplete. Rebuild it:
```powershell
cd C:\Manero-Project\manero\backend
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Frontend won't start — `Cannot find module`**
Dependencies are missing:
```powershell
cd C:\Manero-Project\manero\frontend
npm install
```

**The shop loads but every product is gone**
The database is running but empty — perhaps the data folder was deleted. Recreate it:
```powershell
cd C:\Manero-Project\manero\backend
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m app.seeds.seed_products
```

---

## Related

- Changing products, prices, images, colours → [EDITING.md](EDITING.md)
- Payments, architecture, first-time setup → [README.md](README.md)
