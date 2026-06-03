# 🚀 Deployment Guide - Exercise Detector

## 📋 Prerequisites

- Docker installed ([Download](https://www.docker.com/products/docker-desktop))
- Docker Compose installed
- Trained model saved at `models/trained_model.pkl`
- Git (for cloud deployments)

---

## 🏃 Quick Start - Local Docker

### 1. Build and Run Locally

```bash
# Build Docker image
docker build -t exercise-detector:latest .

# Run container
docker run -p 5000:5000 exercise-detector:latest
```

Or with Docker Compose (easiest):

```bash
# Start
docker-compose up

# Stop
docker-compose down
```

Visit: `http://localhost:5000`

---

## 🌐 Cloud Deployments

### Option 1: Deploy to AWS (EC2)

**Step 1: Create EC2 Instance**
```bash
# AWS CLI
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t2.micro \
  --key-name my-key \
  --security-groups web
```

**Step 2: SSH into instance**
```bash
ssh -i my-key.pem ec2-user@your-instance-ip
```

**Step 3: Setup Docker**
```bash
# Install Docker
sudo yum update -y
sudo amazon-linux-extras install docker -y
sudo systemctl start docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.0.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**Step 4: Clone and run**
```bash
git clone your-repo-url
cd project
docker-compose up -d
```

**Step 5: Configure Security**
- Open port 5000 in Security Group
- Use Elastic IP for static address
- Setup SSL with AWS Certificate Manager

---

### Option 2: Deploy to Google Cloud Run

**Step 1: Setup Google Cloud**
```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

gcloud init
gcloud auth login
```

**Step 2: Create project and enable services**
```bash
gcloud projects create exercise-detector
gcloud config set project exercise-detector
gcloud services enable run.googleapis.com
```

**Step 3: Build and push image**
```bash
# Configure Docker auth
gcloud auth configure-docker

# Build and push
docker build -t gcr.io/exercise-detector/api:latest .
docker push gcr.io/exercise-detector/api:latest
```

**Step 4: Deploy to Cloud Run**
```bash
gcloud run deploy exercise-detector \
  --image gcr.io/exercise-detector/api:latest \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --timeout 3600 \
  --allow-unauthenticated
```

**Result**: Gets a public URL like `https://exercise-detector-xxxxx.run.app`

---

### Option 3: Deploy to Azure Container Instances

**Step 1: Login to Azure**
```bash
az login
```

**Step 2: Create resource group**
```bash
az group create \
  --name exercise-detector-rg \
  --location eastus
```

**Step 3: Create container registry**
```bash
az acr create \
  --resource-group exercise-detector-rg \
  --name exercisedetector \
  --sku Basic

# Login to registry
az acr login --name exercisedetector
```

**Step 4: Build and push image**
```bash
docker build -t exercisedetector.azurecr.io/api:latest .
docker push exercisedetector.azurecr.io/api:latest
```

**Step 5: Deploy container instance**
```bash
az container create \
  --resource-group exercise-detector-rg \
  --name exercise-detector-api \
  --image exercisedetector.azurecr.io/api:latest \
  --cpu 1 --memory 2 \
  --registry-login-server exercisedetector.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --ports 5000 \
  --dns-name-label exercise-detector
```

**Get URL**:
```bash
az container show \
  --resource-group exercise-detector-rg \
  --name exercise-detector-api \
  --query ipAddress.fqdn
```

---

### Option 4: Deploy to Heroku

**Step 1: Install Heroku CLI**
```bash
# https://devcenter.heroku.com/articles/heroku-cli
```

**Step 2: Create Heroku app**
```bash
heroku login
heroku create exercise-detector
```

**Step 3: Add Procfile**
```
# Procfile (create in project root)
web: gunicorn app:app
```

**Step 4: Deploy**
```bash
git push heroku main

# View logs
heroku logs --tail
```

**Result**: Gets URL like `https://exercise-detector.herokuapp.com`

---

### Option 5: Deploy to Railway

**Step 1: Connect GitHub**
- Go to railway.app
- Connect your GitHub account
- Import your repository

**Step 2: Add build command**
```
pip install -r requirements-deploy.txt
```

**Step 3: Add start command**
```
gunicorn app:app
```

**Step 4: Deploy**
- Railway auto-deploys on push
- Gets public URL automatically

---

## 📊 Production Considerations

### Environment Setup
```bash
# Create .env file
cp .env.example .env

# Edit with production values
FLASK_ENV=production
SERVER_PORT=5000
LOG_LEVEL=INFO
```

### Scaling Options

**Vertical Scaling** (more powerful machine):
- Use larger instance type
- 2GB+ RAM recommended
- Multi-core CPU

**Horizontal Scaling** (multiple instances):
```yaml
# docker-compose.yml with load balancer
version: '3.8'
services:
  lb:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
  
  api-1:
    build: .
    environment:
      - WORKER_ID=1
  
  api-2:
    build: .
    environment:
      - WORKER_ID=2
  
  api-3:
    build: .
    environment:
      - WORKER_ID=3
```

### Monitoring & Logging

**CloudWatch (AWS)**:
```bash
# Logs automatically to CloudWatch
# View dashboard: AWS Console → CloudWatch
```

**Google Cloud Logging**:
```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision"
```

**Application Performance**:
```bash
# Track with Datadog/New Relic
pip install datadog newrelic
```

---

## 🔐 Security Checklist

- [ ] Enable HTTPS/SSL
- [ ] Setup authentication/API keys
- [ ] Use environment variables for secrets
- [ ] Implement rate limiting
- [ ] Add request validation
- [ ] Use health checks
- [ ] Monitor for anomalies
- [ ] Regular backups

### Add API Authentication
```python
# In app.py
from functools import wraps
import os

API_KEY = os.getenv('API_KEY')

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        key = request.headers.get('X-API-Key')
        if key != API_KEY:
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/predict', methods=['POST'])
@require_api_key
def predict_from_json():
    # ... existing code
```

---

## 📈 Performance Tuning

### Reduce Model Size
```python
# Quantize model for faster inference
from sklearn.preprocessing import quantile_transform
# ... optimize before serving
```

### Caching
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/predict', methods=['POST'])
@cache.cached(timeout=60)
def predict():
    # ... caching results
```

### Async Processing
```python
# Use Celery for long-running tasks
from celery import Celery

celery = Celery(app.name)

@celery.task
def predict_async(sensor_data):
    return pipeline.predict(sensor_data)
```

---

## 🛠️ Troubleshooting

### Container won't start
```bash
# Check logs
docker logs <container-id>

# Rebuild without cache
docker build --no-cache -t exercise-detector:latest .
```

### Model loading fails
```bash
# Verify model exists
ls -la models/trained_model.pkl

# Verify path is correct in predict_model.py
```

### Out of memory
```bash
# Increase Docker memory
docker run -m 4g exercise-detector:latest

# Or in docker-compose.yml
services:
  exercise-detector:
    mem_limit: 4g
```

---

## 📞 Support & Next Steps

1. **Test API Endpoints**:
   ```bash
   curl -X GET http://localhost:5000/health
   ```

2. **Monitor Performance**:
   - Setup dashboards
   - Set alerts
   - Track metrics

3. **Scale as Needed**:
   - Add more workers
   - Enable auto-scaling
   - Optimize code

4. **Automate Deployment**:
   - Setup CI/CD pipeline
   - Auto-deploy on push
   - Automated testing

---

**You now have a production-ready ML application! 🎉**
