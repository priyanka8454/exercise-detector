import os
import json
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get absolute paths
APP_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(APP_DIR, 'static')

# Import prediction pipeline
from src.models.predict_model import get_pipeline

# Initialize Flask app with absolute static folder path
app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='/static')
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize pipeline on startup (force_reload picks up newly trained model)
try:
    pipeline = get_pipeline(force_reload=True)
    logger.info("✓ ML Pipeline initialized successfully")
except Exception as e:
    logger.error(f"✗ Failed to initialize pipeline: {e}")
    pipeline = None


def _load_demo_sensor_data():
    for name in ('sample_sensor_large.csv', 'sample_bench_press.csv'):
        sample_path = os.path.join(APP_DIR, name)
        if os.path.exists(sample_path):
            return pd.read_csv(sample_path).to_dict(orient='list')
    return None


def _friendly_error(message: str) -> str:
    lower = (message or '').lower()
    if 'missing columns' in lower or 'feature' in lower:
        return 'This file does not look like movement sensor data. Try another file.'
    if 'at least' in lower and 'rows' in lower:
        return 'Not enough movement data. Try a longer recording or use Try demo.'
    if len(message or '') > 120:
        return 'Something went wrong. Please try again or use Try demo.'
    return message or 'Something went wrong. Please try again.'


# ============================================================
# Health & Status Endpoints
# ============================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': pipeline is not None
    }), 200


@app.route('/status', methods=['GET'])
def status():
    """Get detailed status"""
    return jsonify({
        'service': 'Exercise Detector API',
        'version': '1.0.0',
        'status': 'running',
        'model_ready': pipeline is not None,
        'timestamp': datetime.now().isoformat()
    }), 200


# ============================================================
# Prediction Endpoints
# ============================================================

@app.route('/api/predict', methods=['POST'])
def predict_from_json():
    """
    Predict exercise from JSON sensor data
    
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
    if not pipeline:
        return jsonify({'error': 'ML model not loaded'}), 503
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided.'}), 400

        result = pipeline.predict(data)
        if result['success']:
            return jsonify(result), 200
        return jsonify({'error': result.get('error', 'Prediction failed.')}), 400
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500


@app.route('/api/predict-csv', methods=['POST'])
def predict_from_csv():
    """
    Upload CSV file and get prediction
    
    CSV columns: acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z
    """
    if not pipeline:
        return jsonify({'error': 'ML model not loaded'}), 503
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'File must be CSV format'}), 400
        
        # Save uploaded file
        filename = f"{datetime.now().timestamp()}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        df = pd.read_csv(filepath)
        result = pipeline.predict(df)
        
        # Add file info
        result['file'] = filename
        result['rows_processed'] = len(df)
        
        if result['success']:
            return jsonify(result), 200
        return jsonify({'error': _friendly_error(result.get('error', ''))}), 400
    
    except pd.errors.ParserError:
        return jsonify({'error': 'Could not read this file. Please upload a CSV file.'}), 400
    except Exception as e:
        logger.error(f"CSV prediction error: {str(e)}")
        return jsonify({'error': _friendly_error(str(e))}), 500


@app.route('/api/predict-batch', methods=['POST'])
def predict_batch():
    """
    Predict multiple exercises in batch
    
    Expected JSON:
    {
        "data": [
            {"acc_x": [...], "acc_y": [...], ...},
            {"acc_x": [...], "acc_y": [...], ...},
            ...
        ]
    }
    """
    if not pipeline:
        return jsonify({'error': 'ML model not loaded'}), 503
    
    try:
        request_data = request.get_json()
        
        if not request_data or 'data' not in request_data:
            return jsonify({'error': 'Expected JSON with "data" array'}), 400
        
        data_list = request_data['data']
        
        if not isinstance(data_list, list):
            return jsonify({'error': '"data" must be an array'}), 400
        
        results = pipeline.predict_batch(data_list)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'predictions': results
        }), 200
    
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        return jsonify({'error': f'Batch prediction failed: {str(e)}'}), 500


@app.route('/api/predict-demo', methods=['POST'])
def predict_demo():
    """One-click demo using built-in sample workout data."""
    if not pipeline:
        return jsonify({'error': 'The app is not ready yet. Please try again soon.'}), 503

    sensor_data = _load_demo_sensor_data()
    if sensor_data is None:
        return jsonify({'error': 'Demo is not available right now.'}), 503

    result = pipeline.predict(sensor_data)
    if result.get('success'):
        return jsonify(result), 200
    return jsonify({'error': _friendly_error(result.get('error', ''))}), 400


@app.route('/api/sample-sensor', methods=['GET'])
def sample_sensor():
    """Sample sensor JSON for the Advanced tab."""
    sensor_data = _load_demo_sensor_data()
    if sensor_data is None:
        return jsonify({'error': 'Sample not available'}), 404
    return jsonify(sensor_data), 200


# ============================================================
# Frontend Routes
# ============================================================

@app.route('/')
def index():
    """Serve frontend"""
    index_path = os.path.join(STATIC_FOLDER, 'index.html')
    logger.info(f"Serving index from: {index_path}, exists: {os.path.exists(index_path)}")
    
    if not os.path.exists(index_path):
        logger.error(f"Index file not found at {index_path}")
        return jsonify({'error': 'Frontend not found'}), 404
    
    try:
        return send_from_directory(STATIC_FOLDER, 'index.html')
    except Exception as e:
        logger.error(f"Error serving index: {e}")
        # Fallback: read and serve directly
        try:
            with open(index_path, 'r') as f:
                return f.read(), 200, {'Content-Type': 'text/html'}
        except Exception as e2:
            logger.error(f"Fallback failed: {e2}")
            return jsonify({'error': f'Failed to serve frontend: {str(e)}'} ), 500


@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (not API routes)."""
    if filename.startswith('api/'):
        return jsonify({'error': 'Endpoint not found'}), 404
    try:
        return send_from_directory(STATIC_FOLDER, filename)
    except Exception:
        return jsonify({'error': 'File not found'}), 404


# ============================================================
# Error Handlers
# ============================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================
# Main
# ============================================================

if __name__ == '__main__':
    # Development
    app.run(debug=False, host='0.0.0.0', port=5000)
