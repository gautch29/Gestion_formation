# Gestion formation

Web application for managing training modules, personnel, sessions, attendance links, searches, and PDF tracking reports.

## Features

- Create, edit, and delete training modules.
- Create, edit, and delete personnel records.
- Plan a training session with a date, module, instructor, and participants.
- Search sessions by date, personnel, or module.
- Remove a session or remove a personnel/session attendance link.
- Generate a cross-tab PDF report of training completion by personnel and module.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Then open `http://localhost:8000`.

By default the app uses `bdd_formations.db` in the project folder. You can point it to another SQLite file:

```bash
DATABASE_PATH=/path/to/bdd_formations.db python main.py
```

## Run with Docker

```bash
docker compose up --build
```

The container serves the app on `http://localhost:8000` and stores the SQLite database in the `gestion-formation-data` Docker volume. On first start, the volume is seeded from the bundled `bdd_formations.db`.

To build only the image:

```bash
docker build -t gestion-formation .
```

## Pull the published image

GitHub Actions publishes images to GitHub Container Registry.

For this branch:

```bash
docker pull ghcr.io/gautch29/gestion-formation:codex-web-frontend-docker
docker run --rm -p 8000:8000 -v gestion-formation-data:/app/data ghcr.io/gautch29/gestion-formation:codex-web-frontend-docker
```

After the branch is merged to `main`, use `latest`:

```bash
docker pull ghcr.io/gautch29/gestion-formation:latest
docker run --rm -p 8000:8000 -v gestion-formation-data:/app/data ghcr.io/gautch29/gestion-formation:latest
```

With Compose and the published image:

```bash
GESTION_FORMATION_IMAGE=ghcr.io/gautch29/gestion-formation:codex-web-frontend-docker docker compose -f docker-compose.registry.yml up
```

## CI

GitHub Actions runs `.github/workflows/docker-ci.yml` on pushes, pull requests, and manual dispatches. The workflow builds the Docker image, pushes it to GHCR for branch and SHA tags, publishes `latest` from `main`, and validates `docker-compose.yml`.

## Project notes

- `main.py` is the web entrypoint.
- `web_app.py` contains the Flask routes and web view-model assembly.
- `model.py` and `controller.py` keep the original data operations.
- `view.py` is the previous Tkinter UI kept as legacy reference.
