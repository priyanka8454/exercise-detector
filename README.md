# Exercise Detector

AI web app that guesses gym exercises from movement sensor data (CSV upload or demo).

## Run locally

```bash
pip install -r requirements-deploy.txt
python app.py
```

Open http://127.0.0.1:5000

## Deploy

See **[DEPLOY_GITHUB.md](DEPLOY_GITHUB.md)** for GitHub + free cloud hosting (Render).

## Requirements for deploy

- `models/trained_model.pkl` must be in the repo (included)
- Python 3.9+
