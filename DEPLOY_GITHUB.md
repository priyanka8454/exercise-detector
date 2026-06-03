# Deploy Exercise Detector — GitHub + Render (free)

Follow these steps in order. Total time: about 20–30 minutes.

---

## Part 1 — Put code on **your** GitHub

### Step 1: Create a new repository on GitHub

1. Open https://github.com/new  
2. **Repository name:** `exercise-detector` (or any name you like)  
3. **Public**  
4. Do **not** add README, .gitignore, or license (you already have files locally)  
5. Click **Create repository**

### Step 2: Push your project from your PC

Open PowerShell:

```powershell
cd c:\Users\dell\Desktop\template\data-science-template
```

Check remote (you may still point at the original template repo):

```powershell
git remote -v
```

**If you created a new repo under your account**, set your URL (replace `YOUR_USERNAME`):

```powershell
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/exercise-detector.git
```

### Step 3: Commit and push

```powershell
git add app.py static/ src/ models/trained_model.pkl models/LearningAlgorithms.py
git add requirements-deploy.txt render.yaml Procfile README.md DEPLOY_GITHUB.md
git add sample_sensor_large.csv sample_bench_press.csv
git add src/models/input_validation.py src/features/inference_features.py
git add .gitignore .dockerignore Dockerfile docker-compose.yml .env.example
git add quick_train.py save_model.py test_api.py

git status
```

Commit:

```powershell
git commit -m "Add Exercise Detector web app for deployment"
```

Push (first time):

```powershell
git branch -M main
git push -u origin main
```

GitHub may ask you to log in (browser or personal access token).

> **Note:** Large training folders (`data/raw/MetaMotion/`) are not required online. The live site uses `models/trained_model.pkl` only.

---

## Part 2 — Deploy on Render (free website URL)

Render runs your Flask app 24/7 with a public link like `https://exercise-detector-xxxx.onrender.com`.

### Step 1: Sign up

1. Go to https://render.com  
2. Sign up with **GitHub** (easiest)

### Step 2: New Web Service

1. Dashboard → **New +** → **Web Service**  
2. Connect your GitHub account if asked  
3. Select your repo **`exercise-detector`** (or the name you used)

### Step 3: Settings

| Field | Value |
|--------|--------|
| **Name** | `exercise-detector` |
| **Region** | Choose closest to you |
| **Branch** | `main` |
| **Runtime** | `Python 3` (must be **3.11** — repo includes `runtime.txt`) |
| **Build Command** | `pip install -r requirements-deploy.txt` |
| **Start Command** | `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app` |
| **Plan** | Free |

**Environment variable (if build still uses Python 3.14):**  
Render → **Environment** → add `PYTHON_VERSION` = `3.11.9`, then **Manual Deploy** → **Clear build cache & deploy**.

### Step 4: Deploy

1. Click **Create Web Service**  
2. Wait 5–10 minutes for the first build  
3. When status is **Live**, open the URL Render gives you  

### Step 5: Test

- Open your `https://....onrender.com` link  
- Click **Try demo** — should show an exercise  
- Upload a CSV if you have one  

---

## Part 3 — After deploy (important)

### Free tier behavior

- The site **sleeps** after ~15 minutes with no visitors (first click may take 30–60 seconds to wake up).  
- That is normal on Render free plan.

### Custom domain (optional)

Render → your service → **Settings** → **Custom Domain** → follow DNS steps.

### Update the site later

```powershell
cd c:\Users\dell\Desktop\template\data-science-template
git add .
git commit -m "Update app"
git push
```

Render redeploys automatically on each push to `main`.

---

## Alternative: Docker (VPS or any server)

```bash
docker-compose up --build
```

Then open port 5000 (use nginx + HTTPS for production).

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Build fails on Render | Check **Logs** tab; often a missing file — ensure `models/trained_model.pkl` is pushed to GitHub |
| Try demo fails | Open `/health` — if `model_loaded: false`, model file missing on server |
| Push rejected (large files) | Do not push `data/raw/`; use `.gitignore` entries below |
| `gh` not found | Use GitHub website + `git push`; install GitHub CLI optional |

---

## Files that must be on GitHub for deploy

- `app.py`  
- `static/index.html`  
- `src/` (all Python code)  
- `models/trained_model.pkl`  
- `requirements-deploy.txt`  
- `sample_sensor_large.csv` (for demo API)

You do **not** need the full `data/raw/MetaMotion/` folder on GitHub for the website to work.
