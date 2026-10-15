# NaijaFit

A self-hosted app for training at home and eating well on Nigerian food. Answer a few questions
once, and it works out your daily calories and macros, builds a week of bodyweight workouts and a
week of Nigerian meal plans around them, then tracks what you actually do.

Built with **FastAPI + SQLite** on the back end and **Vue 3 + Tailwind** on the front, packaged as
two Docker containers so it deploys to a TrueNAS server with a single command. Locally it runs as
one process on one address.

---

## What it does

- **Onboarding wizard** — seven short steps (about you, body, goal, activity, training, food,
  review). It shows the real calorie and macro numbers before you commit, computed with the same
  maths the app uses afterwards.
- **Targets** — BMR by Mifflin–St Jeor, scaled by activity, then adjusted for your goal. Protein
  per kilo of bodyweight, fat at 25% of calories, carbohydrate for the rest, and a water target.
- **Weekly workout plan** — bodyweight-first home sessions. The split follows how many days you
  chose (3 → full body A/B/C, 4 → upper/lower/pull/conditioning, 5 → push/pull/legs/core/full body,
  6 → push/pull/legs twice), with rest days spread through the week. Every session has a warm-up,
  a main block, a finisher and a cool-down, and is filtered to the equipment you actually have
  (nothing, a chair or step, a resistance band, dumbbells) and your training level.
- **Weekly Nigerian meal plan** — breakfast, lunch, dinner and a snack for all seven days, drawn
  from a library of ~79 Nigerian dishes with per-serving nutrition. Swallows are paired with soups
  (eba + egusi, amala + gbegiri-style, pounded yam + efo riro) and every main meal gets a protein
  anchor, so the day lands near your calorie and protein targets.
- **Food library** — browse and search every dish, filter by category, open one for its full
  nutrition, and add your own family dishes (they're used in future plans).
- **Daily tracking** — mark workouts complete, log meals as you eat them, track water by the glass,
  and record your weight.
- **Progress** — weight trend with your start point, calories eaten over the last 7 days against
  your target, workouts over the last 8 weeks, plus streaks and totals.
- **Backup & restore** — download everything as one file, restore it, or start over completely.

## The Nigerian food library

Around 79 dishes across breakfast, swallows, soups, stews, rice, porridge, proteins, sides, snacks,
fruits and drinks — akara, moi moi, ogi, boiled yam and egg, dodo, eba, pounded yam, semo, amala,
fufu, tuwo, egusi, efo riro, okra, ogbono, bitterleaf, oha, afang, edikang ikong, ofe nsala, banga,
miyan taushe, miyan kuka, obe ata, ayamase, ewa agoyin, beans porridge, jollof, fried rice, ofada,
coconut rice, rice and beans, suya, grilled tilapia, the pepper soups, asun, peppered snail, awara,
ponmo, sardines, chin chin, plantain chips, kuli kuli, puff puff, buns, mango, pawpaw, garden egg,
zobo, chapman, kunu, fura da nono, soy milk and more.

Each dish carries its serving description ("1 wrap (200 g)"), calories, protein, carbohydrate, fat,
fibre and sodium per serving, plus tags used by the planner (`high_protein`, `vegan`, `low_carb`)
and the dietary filters (`gluten`, `dairy`). Dishes you add yourself are marked as yours and are
used in the next plan you generate.

---

## Architecture

```
        ┌──────────────────────────────┐
        │  frontend  (nginx, port 80)   │
        │  serves the Vue app           │
        │  proxies /api                 │
        └───────────────┬──────────────┘
                        │
        ┌───────────────▼──────────────┐
        │  backend  (FastAPI, 8000)     │
        │  REST API + plan generation   │
        │  SQLite database              │
        └───────────────┬──────────────┘
                        │ bind mount
              /mnt/<pool>/naijafit/data/
                 └─ naijafit.db   (profile, plan, logs, custom dishes)
```

Only two containers — no separate database server. Everything lives in one SQLite file, which makes
backup and snapshots on TrueNAS trivial.

---

## Run it on your own computer (no Docker)

One command starts everything. The backend also serves the built interface, so it is a single
process on a single address: **http://localhost:8000**.

1. Install **Python 3.11+** (python.org — tick *Add python.exe to PATH*) and **Node 20+**
   (nodejs.org — use the LTS button).
2. Double-click **`start.cmd`** in the project folder, or run
   `powershell -ExecutionPolicy Bypass -File start.ps1`.

The first run creates a Python environment, installs the dependencies and builds the interface —
a few minutes, with progress shown. After that it starts in seconds and opens your browser.

- **Address:** <http://localhost:8000>
- **Your data:** everything is in `backend/data/naijafit.db`. Copy that file to back up.
- **Stop it:** press Ctrl+C in the window.

> Prefer a hot-reload loop while editing code? Use the two-process setup under *Local development*.

---

## Install on TrueNAS SCALE 24.10+ (one click)

GitHub builds the two images for free, then you install them from the TrueNAS **Apps** screen — no
terminal, no compiling anything yourself.

### The images

`.github/workflows/build-images.yml` builds and publishes them on every push to `main`:

- `ghcr.io/funnydigital/naijafit-backend:latest`
- `ghcr.io/funnydigital/naijafit-frontend:latest`

Because the repository is public the packages are public too, so TrueNAS pulls them with no login.
If you move this into a **private** repo, flip each package to public (profile → **Packages** →
package → **Package settings** → **Change visibility → Public**) or add a registry credential in
TrueNAS.

### One-time: a place for your data

Create a dataset so your data is covered by snapshots — **Datasets → Add Dataset** (for example pool
`tank`, name `apps/naijafit`). Note its path, e.g. `/mnt/tank/apps/naijafit`.

### Install

1. In TrueNAS go to **Apps → Custom App → Install via YAML**.
2. Name it `naijafit`, paste the contents of `deploy/truenas-custom-app.yaml` — the image paths are
   already filled in — and change the data path to your dataset.
3. Click **Install**. TrueNAS pulls the images and starts both containers.
4. Open `http://<truenas-ip>:8080` and walk through onboarding.

**Updating later:** push a change to GitHub; when the workflow finishes, open the app in TrueNAS and
press **Restart** — `pull_policy: always` fetches the newest `latest`.

> Want a domain name or HTTPS? Point your existing reverse proxy at `http://<truenas-ip>:8080`.

---

## Alternative: build on the server over SSH

Prefer not to use GitHub? Copy the project to the NAS and build it there instead.

```bash
scp -r naijafit admin@<truenas-ip>:/mnt/tank/apps/naijafit
ssh admin@<truenas-ip>
cd /mnt/tank/apps/naijafit
cp .env.example .env          # then edit DATA_DIR to your dataset
docker compose up -d --build
docker compose logs -f
```

Open `http://<truenas-ip>:8080`. To update later: `git pull`, then
`docker compose up -d --build`.

---

## Local development

Run the two halves separately for a fast edit-reload loop.

**Backend** (Python 3.11 or 3.12):

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

```bash
# Linux / macOS
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The food and exercise catalogs seed themselves on first start. API docs are at
<http://localhost:8000/docs>.

**Frontend** (Node 20+):

```bash
cd frontend
npm install --include=dev
npm run dev
```

Open <http://localhost:5173>. Vite proxies `/api` to the backend on port 8000.

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `FRONTEND_PORT` | `8080` | Host port the site is served on (Docker only) |
| `DATA_DIR` | `./data` | Folder holding `naijafit.db` |
| `SITE_TITLE` | `NaijaFit` | Shown in the header and browser tab |

---

## API reference (short)

Meta: `GET /api/site`, `GET /api/onboarding/options`.

Profile: `GET /api/profile`, `PUT /api/profile` (saves, recomputes targets and rebuilds the plan),
`POST /api/profile/preview` (targets for a set of answers, without saving), `GET /api/targets`.

Catalog: `GET /api/foods` (filter by `category`, `tag`, `slot`, `q`), `GET /api/foods/{id}`,
`POST/PUT/DELETE /api/foods`, `GET /api/exercises` (filter by `category`, `equipment`, `level`, `q`).

Plan: `GET /api/plan`, `POST /api/plan/generate`, `GET /api/plan/workout/{day_index}`,
`GET /api/plan/meals/{day_index}`, `POST /api/plan/meals/{meal_id}/swap`.

Logs: `POST/GET/DELETE /api/logs/workout`, `POST/GET/DELETE /api/logs/meal`,
`POST/GET /api/logs/weight`, `POST/GET /api/logs/water`, `GET /api/dashboard?date=YYYY-MM-DD`.

Data: `GET /api/admin/backup`, `POST /api/admin/restore`, `DELETE /api/admin/data`.

Full interactive docs at `/docs`.

---

## Project structure

```
naijafit/
├── start.cmd / start.ps1       # run it locally, one command, no Docker
├── docker-compose.yml
├── .env.example
├── deploy/
│   └── truenas-custom-app.yaml # paste into TrueNAS → Apps → Custom App
├── .github/workflows/
│   └── build-images.yml        # builds + publishes both images to GHCR
├── backend/
│   ├── Dockerfile, entrypoint.sh, requirements.txt
│   └── app/
│       ├── main.py             # FastAPI app, mounts the built interface
│       ├── config.py           # env config + data paths
│       ├── database.py         # SQLAlchemy engine (SQLite + WAL + foreign keys)
│       ├── models.py           # Profile, Food, Exercise, PlanWorkout/Item, PlanMeal, logs
│       ├── schemas.py          # request models
│       ├── serializers.py      # API response shapes
│       ├── nutrition.py        # BMR / TDEE / macros / water
│       ├── workoutplanner.py   # weekly split generator
│       ├── mealplanner.py      # Nigerian meal generator
│       ├── generate.py         # apply targets + rebuild the plan
│       ├── seed.py             # fills the catalogs on first start
│       ├── data/
│       │   ├── foods.json      # ~79 Nigerian dishes with per-serving nutrition
│       │   └── exercises.json  # ~88 home exercises
│       └── routes/             # meta, options, profile, foods, exercises, plan, logs, dashboard, admin
└── frontend/
    ├── Dockerfile, nginx.conf, vite.config.js, tailwind.config.js
    └── src/
        ├── router/
        ├── services/api.js
        ├── composables/        # useProfile, useDashboard, useOnboarding, useToast, useReveal
        ├── utils/              # dates + unit formatting
        ├── components/         # Icon, AppHeader, TabBar, DishRow, FoodTile, StatRing, charts…
        └── views/              # Onboarding (+7 steps), Today, Workouts, WorkoutDetail, Meals,
                                # Foods, FoodDetail, Progress, Profile
```

## Notes

- The app is single-user by design: one profile, one plan, one set of logs. There is no login, so
  put it behind your reverse proxy's auth if you expose it to the internet.
- Nutrition values are per stated serving and are realistic approximations for planning, not a
  clinical database.
- Plans are generated with a seed derived from your profile, so regenerating without changing
  anything gives you the same week. Change a detail (or your equipment) and you get a fresh one.
- Dinner is the same plan as lunch's categories but rotated — the plan is a guide, not a
  prescription. Swap any dish you don't fancy; logs are always yours to edit.
