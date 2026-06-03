# ⚡ QUICK START - Run Full Stack in 5 Minutes

## Step 1: Train & Save Your Model (2 min)

First, you need to run `train_model.py` to save the trained model:

```bash
cd src/models
python train_model.py
# Wait for training to complete...
```

This creates: `models/trained_model.pkl` ✓

**Or copy this code at the END of your train_model.py:**
```python
# At end of src/models/train_model.py
import joblib

# Save best model
joblib.dump(best_model, "../models/trained_model.pkl")
print("✓ Model saved to models/trained_model.pkl")
```

---

## Step 2: Install Dependencies (1 min)

```bash
pip install -r requirements-deploy.txt
```

---

## Step 3: Run Locally (No Docker)

```bash
cd c:\Users\dell\Desktop\template\data-science-template
python app.py
```

Visit: **http://localhost:5000**

---

## Step 4: Test the API

### Test with CSV
1. Open http://localhost:5000
2. Upload a CSV file with columns: acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z
3. Click "Analyze CSV"
4. See results!

### Test with JSON
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "acc_x": [1.2, 1.3, 1.4],
    "acc_y": [0.5, 0.6, 0.7],
    "acc_z": [9.8, 9.9, 9.7],
    "gyro_x": [0.1, 0.2, 0.1],
    "gyro_y": [0.0, 0.1, 0.0],
    "gyro_z": [0.3, 0.2, 0.4]
  }'
```

### Test Health Check
```bash
curl http://localhost:5000/health
```

---

## 🐳 Run with Docker (Optional)

### Option A: Docker Compose (Easiest)
```bash
docker-compose up
```

### Option B: Plain Docker
```bash
docker build -t exercise-detector:latest .
docker run -p 5000:5000 exercise-detector:latest
```

---

## 🚀 Deploy to Cloud (Choose One)

### 🟦 Deploy to Google Cloud Run (Recommended - Free tier available)
```bash
# Install gcloud CLI
# Then run:
gcloud run deploy exercise-detector \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### ☁️ Deploy to AWS EC2
```bash
# Create EC2 instance, SSH in, then:
git clone your-repo
cd project
docker-compose up -d
```

### 🟠 Deploy to Azure
```bash
az container create \
  --resource-group my-group \
  --name exercise-detector \
  --image my-registry.azurecr.io/api:latest \
  --ports 5000 \
  --cpu 1 --memory 2
```

### 🚁 Deploy to Heroku
```bash
heroku login
heroku create exercise-detector
git push heroku main
```

---

## 📁 Project Structure After Setup

```
data-science-template/
├── app.py                          ✓ Flask backend
├── static/
│   └── index.html                  ✓ Web UI
├── src/
│   ├── models/
│   │   ├── train_model.py          ✓ Training script
│   │   └── predict_model.py        ✓ Prediction pipeline
│   ├── features/
│   │   └── count_repetitions.py   ✓ Rep counter
│   └── ...
├── models/
│   └── trained_model.pkl           ✓ Saved model
├── Dockerfile                      ✓ Container config
├── docker-compose.yml              ✓ Docker Compose
├── requirements-deploy.txt         ✓ Dependencies
└── DEPLOYMENT_GUIDE.md            ✓ Full deployment docs
```

---

## 🧪 Test CSV Sample

Save as `test_data.csv`:
```csv
acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z
1.2,0.5,9.8,0.1,0.0,0.3
1.3,0.6,9.9,0.2,0.1,0.2
1.4,0.7,9.7,0.1,0.0,0.4
1.5,0.8,10.0,0.15,0.05,0.35
1.4,0.7,9.8,0.12,0.02,0.32
```

Upload to http://localhost:5000 → Get exercise prediction!

---

## ✅ Checklist

- [ ] Run train_model.py to save model
- [ ] `pip install -r requirements-deploy.txt`
- [ ] `python app.py` works locally
- [ ] Visit http://localhost:5000 ✓
- [ ] Upload CSV → See prediction ✓
- [ ] Ready to deploy! 🚀

---

## 🎯 What to Do Next

### Production-Ready Steps:
1. Add authentication (API keys)
2. Setup monitoring & logging
3. Enable HTTPS/SSL
4. Setup auto-scaling
5. Add rate limiting

See **DEPLOYMENT_GUIDE.md** for detailed instructions!

---

## 🆘 Troubleshooting

**Model not found?**
```bash
# Make sure you ran train_model.py and it saved the model
ls models/trained_model.pkl
```

**Port 5000 already in use?**
```bash
# Change port in app.py
app.run(port=8000)  # Use 8000 instead
```

**Dependencies error?**
```bash
# Reinstall
pip install --upgrade --force-reinstall -r requirements-deploy.txt
```

---

**You're ready to go! 🎉 Visit http://localhost:5000**
