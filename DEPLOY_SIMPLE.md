# Deploy Exercise Detector (simple guide)

## Before deploy

1. Train and save the model (same Python version you deploy with):

```powershell
cd data-science-template
$env:PYTHONIOENCODING='utf-8'
python quick_train.py
```

2. Confirm these exist:
   - `models/trained_model.pkl`
   - `data/interim/03_data_features.pkl` (for retraining)

---

## Option A — Docker (recommended)

```powershell
cd data-science-template
docker-compose up --build
```

Open `http://localhost:5000`

To run in background: `docker-compose up -d --build`

---

## Option B — Render.com (free tier)

1. Push the project to GitHub.
2. On [render.com](https://render.com): **New → Web Service** → connect repo.
3. Settings:
   - **Root directory:** `data-science-template`
   - **Build command:** `pip install -r requirements-deploy.txt && python quick_train.py`
   - **Start command:** `gunicorn -w 2 -b 0.0.0.0:5000 app:app`
4. Add env var `PYTHONIOENCODING=utf-8`
5. Deploy. Use the URL Render gives you.

---

## Option C — Railway

1. Push to GitHub.
2. [railway.app](https://railway.app) → New Project → Deploy from GitHub.
3. Set root to `data-science-template`.
4. Start command: `gunicorn -w 2 -b 0.0.0.0:$PORT app:app` (Railway sets `PORT`).
5. Include `models/trained_model.pkl` in the repo or run `quick_train.py` in build.

---

## Option D — VPS (Ubuntu)

```bash
git clone <your-repo>
cd data-science-template
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-deploy.txt
python quick_train.py
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

Use **nginx** as reverse proxy and **HTTPS** (Let's Encrypt) for production.

---

## Production checklist

- [ ] Model trained with same `scikit-learn` as server
- [ ] Do not use Flask dev server (`python app.py`) in production — use **gunicorn**
- [ ] Open only port 80/443 (not raw 5000) behind a reverse proxy
- [ ] Max upload 16MB (already set in `app.py`)

Full details: `DEPLOYMENT_GUIDE.md`
