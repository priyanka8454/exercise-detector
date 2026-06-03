"""
API Testing & Documentation Script
Run this to test all endpoints
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:5000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    END = '\033[0m'

def print_test(name):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}🧪 TEST: {name}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.YELLOW}ℹ {msg}{Colors.END}")

def test_health():
    """Test health endpoint"""
    print_test("Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print_info(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print_success("Health check passed!")
            return True
        else:
            print_error("Unexpected status code")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server. Is it running?")
        print_info("Run: python app.py")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_json_prediction():
    """Test JSON prediction"""
    print_test("JSON Prediction")
    
    data = {
        "acc_x": [1.2, 1.3, 1.4, 1.5, 1.4, 1.3, 1.2, 1.1],
        "acc_y": [0.5, 0.6, 0.7, 0.8, 0.7, 0.6, 0.5, 0.4],
        "acc_z": [9.8, 9.9, 9.7, 10.0, 9.8, 9.7, 9.9, 9.8],
        "gyro_x": [0.1, 0.2, 0.1, 0.15, 0.12, 0.1, 0.2, 0.15],
        "gyro_y": [0.0, 0.1, 0.0, 0.05, 0.02, 0.0, 0.1, 0.05],
        "gyro_z": [0.3, 0.2, 0.4, 0.35, 0.32, 0.3, 0.2, 0.25]
    }
    
    print_info(f"Sending {len(data['acc_x'])} data points...")
    print(json.dumps({k: f"[{len(v)} values]" for k, v in data.items()}, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/predict",
            json=data,
            timeout=30
        )
        
        print_info(f"Status: {response.status_code}")
        result = response.json()
        print(json.dumps(result, indent=2))
        
        if response.status_code == 200 and result.get('success'):
            print_success("Prediction successful!")
            print_success(f"Exercise: {result['exercise']}")
            print_success(f"Confidence: {result['confidence_percent']}%")
            if result.get('reps'):
                print_success(f"Estimated reps: {result['reps']}")
            return True
        else:
            print_error("Prediction failed")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_csv_prediction():
    """Test CSV prediction"""
    print_test("CSV File Upload")
    
    # Create test CSV
    csv_path = Path("test_sensor_data.csv")
    csv_content = """acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z
1.2,0.5,9.8,0.1,0.0,0.3
1.3,0.6,9.9,0.2,0.1,0.2
1.4,0.7,9.7,0.1,0.0,0.4
1.5,0.8,10.0,0.15,0.05,0.35
1.4,0.7,9.8,0.12,0.02,0.32
1.3,0.6,9.9,0.1,0.0,0.3
1.2,0.5,9.8,0.2,0.1,0.25
1.1,0.4,9.7,0.15,0.05,0.3
"""
    
    with open(csv_path, 'w') as f:
        f.write(csv_content)
    
    print_info(f"Created test CSV: {csv_path}")
    
    try:
        with open(csv_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{BASE_URL}/api/predict-csv",
                files=files,
                timeout=30
            )
        
        print_info(f"Status: {response.status_code}")
        result = response.json()
        print(json.dumps(result, indent=2))
        
        if response.status_code == 200 and result.get('success'):
            print_success("CSV prediction successful!")
            print_success(f"Exercise: {result['exercise']}")
            print_success(f"Rows processed: {result.get('rows_processed', 'N/A')}")
            return True
        else:
            print_error("CSV prediction failed")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False
    finally:
        # Cleanup
        if csv_path.exists():
            csv_path.unlink()

def test_batch_prediction():
    """Test batch prediction"""
    print_test("Batch Prediction")
    
    batch_data = {
        "data": [
            {
                "acc_x": [1.2, 1.3, 1.4],
                "acc_y": [0.5, 0.6, 0.7],
                "acc_z": [9.8, 9.9, 9.7],
                "gyro_x": [0.1, 0.2, 0.1],
                "gyro_y": [0.0, 0.1, 0.0],
                "gyro_z": [0.3, 0.2, 0.4]
            },
            {
                "acc_x": [1.0, 1.1, 1.2],
                "acc_y": [0.3, 0.4, 0.5],
                "acc_z": [9.7, 9.8, 9.9],
                "gyro_x": [0.05, 0.15, 0.1],
                "gyro_y": [-0.05, 0.05, 0.0],
                "gyro_z": [0.2, 0.3, 0.25]
            }
        ]
    }
    
    print_info("Sending 2 samples for batch prediction...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/predict-batch",
            json=batch_data,
            timeout=30
        )
        
        print_info(f"Status: {response.status_code}")
        result = response.json()
        print(json.dumps(result, indent=2))
        
        if response.status_code == 200 and result.get('success'):
            print_success(f"Batch prediction successful!")
            print_success(f"Predictions count: {result.get('count', 0)}")
            return True
        else:
            print_error("Batch prediction failed")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def main():
    print(f"\n{Colors.YELLOW}")
    print("="*60)
    print("🧪 API Testing Suite")
    print("="*60)
    print(f"{Colors.END}")
    
    print_info(f"Base URL: {BASE_URL}")
    print_info("Make sure the server is running: python app.py")
    
    time.sleep(2)
    
    results = {}
    
    # Run tests
    results['health'] = test_health()
    
    if results['health']:
        results['json'] = test_json_prediction()
        results['csv'] = test_csv_prediction()
        results['batch'] = test_batch_prediction()
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}📊 TEST SUMMARY{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_flag in results.items():
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed_flag else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"{test_name.upper():15} {status}")
    
    print(f"\n{Colors.YELLOW}Total: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print(f"{Colors.GREEN}\n✅ All tests passed! API is ready for use.{Colors.END}")
        return 0
    else:
        print(f"{Colors.RED}\n❌ Some tests failed. Check the errors above.{Colors.END}")
        return 1

if __name__ == "__main__":
    exit(main())
