# 🔧 Implementation Guide - Build Your Frontend

## Quick Start: 3 Files to Complete Your Project

### FILE 1: Complete predict_model.py
Create: `src/models/predict_model.py`

```python
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

class ExercisePredictionPipeline:
    """Load model and make predictions on new sensor data"""
    
    def __init__(self, model_path="../models/trained_model.pkl"):
        self.model = joblib.load(model_path)
        self.scaler = StandardScaler()
    
    def preprocess_sensor_data(self, sensor_dict):
        """
        Convert raw sensor readings to feature vector
        
        Input: {
            'acc_x': [1.2, 1.3, ...],
            'acc_y': [0.5, 0.6, ...],
            'acc_z': [9.8, 9.7, ...],
            'gyro_x': [0.1, 0.2, ...],
            'gyro_y': [0.0, 0.1, ...],
            'gyro_z': [0.3, 0.2, ...]
        }
        """
        df = pd.DataFrame(sensor_dict)
        
        # Compute derived features
        df['acc_r'] = np.sqrt(df['acc_x']**2 + df['acc_y']**2 + df['acc_z']**2)
        df['gyro_r'] = np.sqrt(df['gyro_x']**2 + df['gyro_y']**2 + df['gyro_z']**2)
        
        # Return only feature columns (36+ features from training)
        return df
    
    def predict(self, sensor_data):
        """
        Args:
            sensor_data: dict or DataFrame with accelerometer & gyroscope readings
        
        Returns:
            {'exercise': 'bench', 'confidence': 0.95, 'reps': 8}
        """
        # Preprocess
        df = self.preprocess_sensor_data(sensor_data)
        
        # Make prediction
        prediction = self.model.predict(df)
        probabilities = self.model.predict_proba(df)
        confidence = np.max(probabilities)
        
        exercises = ['bench', 'squat', 'row', 'ohp', 'dead']
        
        return {
            'exercise': exercises[prediction[0]],
            'confidence': float(confidence),
            'all_probabilities': {exercises[i]: float(p) for i, p in enumerate(probabilities[0])}
        }

# Initialize globally
pipeline = ExercisePredictionPipeline()
```

---

### FILE 2: Create Flask Backend
Create: `app.py` (in project root)

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import json
from src.models.predict_model import pipeline

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests for frontend

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict exercise from sensor data
    
    Expected JSON:
    {
        "acc_x": [1.2, 1.3, 1.4, ...],
        "acc_y": [0.5, 0.6, 0.7, ...],
        "acc_z": [9.8, 9.9, 9.7, ...],
        "gyro_x": [0.1, 0.2, 0.1, ...],
        "gyro_y": [0.0, 0.1, 0.0, ...],
        "gyro_z": [0.3, 0.2, 0.4, ...]
    }
    """
    try:
        data = request.json
        result = pipeline.predict(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/predict-from-csv', methods=['POST'])
def predict_from_csv():
    """Upload CSV file and get prediction"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        df = pd.read_csv(file)
        
        # Convert to dict format
        sensor_data = df.to_dict(orient='list')
        
        result = pipeline.predict(sensor_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/predict-batch', methods=['POST'])
def predict_batch():
    """Predict multiple exercises"""
    try:
        data_list = request.json  # Array of sensor data
        results = [pipeline.predict(data) for data in data_list]
        return jsonify({'predictions': results}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

---

### FILE 3: Create Simple HTML Frontend
Create: `frontend.html` (or put in `static/index.html`)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏋️ Exercise Detector</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 500px;
            width: 100%;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            text-align: center;
        }
        .subtitle {
            color: #666;
            text-align: center;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .upload-area {
            border: 2px dashed #667eea;
            border-radius: 10px;
            padding: 30px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 20px;
        }
        .upload-area:hover {
            background: #f0f4ff;
            border-color: #764ba2;
        }
        .upload-area.drag-over {
            background: #e8f0ff;
            border-color: #764ba2;
            transform: scale(1.02);
        }
        input[type="file"] {
            display: none;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            width: 100%;
            transition: all 0.3s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .result {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9ff;
            border-radius: 10px;
            display: none;
        }
        .result.show {
            display: block;
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .result-item {
            margin: 15px 0;
        }
        .result-label {
            color: #666;
            font-size: 14px;
            font-weight: 500;
        }
        .result-value {
            color: #667eea;
            font-size: 24px;
            font-weight: bold;
        }
        .confidence-bar {
            background: #e0e0e0;
            height: 8px;
            border-radius: 10px;
            margin-top: 8px;
            overflow: hidden;
        }
        .confidence-fill {
            background: linear-gradient(90deg, #667eea, #764ba2);
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s;
        }
        .error {
            background: #ffe0e0;
            color: #c00;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            display: none;
        }
        .error.show {
            display: block;
        }
        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏋️ Exercise Detector</h1>
        <p class="subtitle">Upload sensor data to identify exercise type</p>
        
        <div class="upload-area" id="uploadArea">
            <p style="font-size: 40px; margin-bottom: 10px;">📁</p>
            <p style="font-weight: 600; color: #333;">Click to upload CSV</p>
            <p style="font-size: 12px; color: #999; margin-top: 5px;">or drag and drop</p>
            <input type="file" id="fileInput" accept=".csv">
        </div>
        
        <button class="btn" id="predictBtn" disabled>Predict Exercise</button>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p style="margin-top: 10px; color: #666;">Analyzing...</p>
        </div>
        
        <div class="result" id="result">
            <div class="result-item">
                <div class="result-label">Detected Exercise:</div>
                <div class="result-value" id="exerciseResult">-</div>
            </div>
            <div class="result-item">
                <div class="result-label">Confidence:</div>
                <div class="result-value" id="confidenceResult">-</div>
                <div class="confidence-bar">
                    <div class="confidence-fill" id="confidenceFill"></div>
                </div>
            </div>
            <div class="result-item" id="probabilitiesDiv" style="display: none;">
                <div class="result-label">All Probabilities:</div>
                <div id="probabilities"></div>
            </div>
        </div>
        
        <div class="error" id="error"></div>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const predictBtn = document.getElementById('predictBtn');
        const result = document.getElementById('result');
        const error = document.getElementById('error');
        const loading = document.getElementById('loading');
        let selectedFile = null;

        // File selection
        uploadArea.addEventListener('click', () => fileInput.click());
        
        fileInput.addEventListener('change', (e) => {
            selectedFile = e.target.files[0];
            if (selectedFile) {
                uploadArea.style.borderColor = '#667eea';
                predictBtn.disabled = false;
            }
        });

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            selectedFile = e.dataTransfer.files[0];
            fileInput.files = e.dataTransfer.files;
            if (selectedFile) predictBtn.disabled = false;
        });

        // Predict
        predictBtn.addEventListener('click', async () => {
            if (!selectedFile) return;
            
            loading.style.display = 'block';
            result.classList.remove('show');
            error.classList.remove('show');
            
            const formData = new FormData();
            formData.append('file', selectedFile);
            
            try {
                const response = await fetch('http://localhost:5000/predict-from-csv', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    document.getElementById('exerciseResult').textContent = 
                        data.exercise.toUpperCase();
                    document.getElementById('confidenceResult').textContent = 
                        (data.confidence * 100).toFixed(1) + '%';
                    document.getElementById('confidenceFill').style.width = 
                        (data.confidence * 100) + '%';
                    
                    // Show all probabilities
                    const probHtml = Object.entries(data.all_probabilities)
                        .map(([ex, prob]) => `${ex}: ${(prob*100).toFixed(1)}%`)
                        .join('<br>');
                    document.getElementById('probabilities').innerHTML = probHtml;
                    
                    result.classList.add('show');
                } else {
                    throw new Error(data.error || 'Prediction failed');
                }
            } catch (err) {
                error.textContent = '❌ ' + err.message;
                error.classList.add('show');
            } finally {
                loading.style.display = 'none';
            }
        });
    </script>
</body>
</html>
```

---

## 🚀 How to Run Everything

### Step 1: Install Flask
```bash
pip install flask flask-cors
```

### Step 2: Run Backend
```bash
python app.py
```
Backend runs on: `http://localhost:5000`

### Step 3: Open Frontend
- Save `frontend.html` to your desktop
- Open in browser
- Upload a CSV file with sensor data
- Click "Predict Exercise"

---

## 📝 CSV File Format Expected

Your CSV should have these columns:
```
acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z
1.2,0.5,9.8,0.1,0.0,0.3
1.3,0.6,9.9,0.2,0.1,0.2
1.4,0.7,9.7,0.1,0.0,0.4
...
```

---

## ✅ Checklist to Complete Your Project

- [ ] Run `train_model.py` fully (saves model to `models/trained_model.pkl`)
- [ ] Copy **FILE 1** code to `src/models/predict_model.py`
- [ ] Copy **FILE 2** code to `app.py` in project root
- [ ] Copy **FILE 3** code to `frontend.html`
- [ ] Install Flask: `pip install flask flask-cors`
- [ ] Start Flask app: `python app.py`
- [ ] Open `frontend.html` in browser
- [ ] Test with your sensor data CSV

Done! You now have a complete full-stack ML project! 🎉
