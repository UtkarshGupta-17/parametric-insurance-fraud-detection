import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_legitimate_claim():
    """Test with a legitimate claim"""
    print("\n✅ TEST 1: LEGITIMATE CLAIM")
    print("=" * 50)
    
    claim = {
        "user_id": "user_legitimate_001",
        "claim_amount": 500,
        "region": "downtown_area",
        "gps_accuracy": 15,  # Good accuracy
        "signal_quality": 0.92,  # Good signal
        "accelerometer_data": 0.85,  # Good sensor data
        "battery_drain": 8,  # Normal battery drain
        "app_foreground_time": 85,  # App was active
        "latency_ms": 45,  # Good latency
        "device_id": "device_001",
        "ip_address": "192.168.1.100",
        "duration": 15,
        "gps_history": [
            {"lat": 40.7128, "lon": -74.0060, "timestamp": 1704067200},
            {"lat": 40.7129, "lon": -74.0061, "timestamp": 1704067260}
        ],
        "curr_location": {"lat": 40.7129, "lon": -74.0061},
        "prev_location": {"lat": 40.7128, "lon": -74.0060},
        "time_diff_minutes": 1,
        "gps_movement": 0.15
    }
    
    response = requests.post(f"{BASE_URL}/submit-claim", json=claim)
    result = response.json()
    
    print(f"Status: {result['status']}")
    print(f"Risk Level: {result['risk_assessment']['risk_level']}")
    print(f"Risk Score: {result['risk_assessment']['final_risk_score']}")
    print(f"Recommendation: {result['action']['message']}")
    print(f"Action: {result['action']['type']}")

def test_suspicious_claim():
    """Test with a suspicious claim (spoofing indicators)"""
    print("\n⚠️  TEST 2: SUSPICIOUS CLAIM (SPOOFING)")
    print("=" * 50)
    
    claim = {
        "user_id": "user_suspicious_002",
        "claim_amount": 500,
        "region": "downtown_area",
        "gps_accuracy": 150,  # Poor accuracy
        "signal_quality": 0.99,  # Too perfect
        "accelerometer_data": 0.05,  # No sensor movement
        "battery_drain": 0,  # No battery drain despite activity
        "app_foreground_time": 15,  # App barely used
        "latency_ms": 180,  # High latency
        "device_id": "device_spoofed",
        "ip_address": "10.0.0.1",
        "duration": 30,
        "gps_history": [
            {"lat": 40.7128, "lon": -74.0060, "timestamp": 1704067200},
            {"lat": 40.7130, "lon": -74.0062, "timestamp": 1704067210},
            {"lat": 40.7132, "lon": -74.0064, "timestamp": 1704067220}
        ],
        "curr_location": {"lat": 40.7150, "lon": -74.0080},
        "prev_location": {"lat": 40.7128, "lon": -74.0060},
        "time_diff_minutes": 0.5,
        "gps_movement": 0.05
    }
    
    response = requests.post(f"{BASE_URL}/submit-claim", json=claim)
    result = response.json()
    
    print(f"Status: {result['status']}")
    print(f"Risk Level: {result['risk_assessment']['risk_level']}")
    print(f"Risk Score: {result['risk_assessment']['final_risk_score']}")
    print(f"Recommendation: {result['action']['message']}")
    print(f"Action: {result['action']['type']}")

def test_fraud_ring():
    """Test fraud ring detection"""
    print("\n🔴 TEST 3: FRAUD RING DETECTION")
    print("=" * 50)
    
    fraud_ring_check = {
        "user_id": "user_fraud_ring_003",
        "ip_address": "192.168.1.50",
        "device_id": "device_shared",
        "region": "downtown_area",
        "timestamp": datetime.now().timestamp()
    }
    
    response = requests.post(f"{BASE_URL}/fraud-ring-check", json=fraud_ring_check)
    result = response.json()
    
    print(f"Fraud Ring Detected: {result['fraud_ring_detected']}")
    print(f"Fraud Ring Score: {result['fraud_ring_score']}")
    print(f"Severity: {result['severity']}")

def test_user_claims():
    """Get user's claims history"""
    print("\n📋 TEST 4: USER CLAIMS HISTORY")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/user-claims/user_legitimate_001")
    result = response.json()
    
    print(f"User ID: {result['user_id']}")
    print(f"Total Claims: {result['total_claims']}")

def test_health():
    """Test health check"""
    print("\n💚 TEST 5: HEALTH CHECK")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/health")
    result = response.json()
    
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("🔐 ANTI-SPOOFING FRAUD DETECTION - API TESTS")
    print("=" * 50)
    
    try:
        test_health()
        test_legitimate_claim()
        test_suspicious_claim()
        test_fraud_ring()
        test_user_claims()
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 50 + "\n")
    
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server.")
        print("Make sure the Flask app is running: python app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_legitimate_claim():
    """Test with a legitimate claim"""
    print("\n✅ TEST 1: LEGITIMATE CLAIM")
    print("=" * 50)
    
    claim = {
        "user_id": "user_legitimate_001",
        "claim_amount": 500,
        "region": "downtown_area",
        "gps_accuracy": 15,  # Good accuracy
        "signal_quality": 0.92,  # Good signal
        "accelerometer_data": 0.85,  # Good sensor data
        "battery_drain": 8,  # Normal battery drain
        "app_foreground_time": 85,  # App was active
        "latency_ms": 45,  # Good latency
        "device_id": "device_001",
        "ip_address": "192.168.1.100",
        "duration": 15,
        "gps_history": [
            {"lat": 40.7128, "lon": -74.0060, "timestamp": 1704067200},
            {"lat": 40.7129, "lon": -74.0061, "timestamp": 1704067260}
        ],
        "curr_location": {"lat": 40.7129, "lon": -74.0061},
        "prev_location": {"lat": 40.7128, "lon": -74.0060},
        "time_diff_minutes": 1,
        "gps_movement": 0.15
    }
    
    response = requests.post(f"{BASE_URL}/submit-claim", json=claim)
    result = response.json()
    
    print(f"Status: {result['status']}")
    print(f"Risk Level: {result['risk_assessment']['risk_level']}")
    print(f"Risk Score: {result['risk_assessment']['final_risk_score']}")
    print(f"Recommendation: {result['action']['message']}")
    print(f"Action: {result['action']['type']}")

def test_suspicious_claim():
    """Test with a suspicious claim (spoofing indicators)"""
    print("\n⚠️  TEST 2: SUSPICIOUS CLAIM (SPOOFING)")
    print("=" * 50)
    
    claim = {
        "user_id": "user_suspicious_002",
        "claim_amount": 500,
        "region": "downtown_area",
        "gps_accuracy": 150,  # Poor accuracy
        "signal_quality": 0.99,  # Too perfect
        "accelerometer_data": 0.05,  # No sensor movement
        "battery_drain": 0,  # No battery drain despite activity
        "app_foreground_time": 15,  # App barely used
        "latency_ms": 180,  # High latency
        "device_id": "device_spoofed",
        "ip_address": "10.0.0.1",
        "duration": 30,
        "gps_history": [
            {"lat": 40.7128, "lon": -74.0060, "timestamp": 1704067200},
            {"lat": 40.7130, "lon": -74.0062, "timestamp": 1704067210},
            {"lat": 40.7132, "lon": -74.0064, "timestamp": 1704067220}
        ],
        "curr_location": {"lat": 40.7150, "lon": -74.0080},
        "prev_location": {"lat": 40.7128, "lon": -74.0060},
        "time_diff_minutes": 0.5,
        "gps_movement": 0.05
    }
    
    response = requests.post(f"{BASE_URL}/submit-claim", json=claim)
    result = response.json()
    
    print(f"Status: {result['status']}")
    print(f"Risk Level: {result['risk_assessment']['risk_level']}")
    print(f"Risk Score: {result['risk_assessment']['final_risk_score']}")
    print(f"Recommendation: {result['action']['message']}")
    print(f"Action: {result['action']['type']}")

def test_fraud_ring():
    """Test fraud ring detection"""
    print("\n🔴 TEST 3: FRAUD RING DETECTION")
    print("=" * 50)
    
    fraud_ring_check = {
        "user_id": "user_fraud_ring_003",
        "ip_address": "192.168.1.50",
        "device_id": "device_shared",
        "region": "downtown_area",
        "timestamp": datetime.now().timestamp()
    }
    
    response = requests.post(f"{BASE_URL}/fraud-ring-check", json=fraud_ring_check)
    result = response.json()
    
    print(f"Fraud Ring Detected: {result['fraud_ring_detected']}")
    print(f"Fraud Ring Score: {result['fraud_ring_score']}")
    print(f"Severity: {result['severity']}")

def test_user_claims():
    """Get user's claims history"""
    print("\n📋 TEST 4: USER CLAIMS HISTORY")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/user-claims/user_legitimate_001")
    result = response.json()
    
    print(f"User ID: {result['user_id']}")
    print(f"Total Claims: {result['total_claims']}")

def test_health():
    """Test health check"""
    print("\n💚 TEST 5: HEALTH CHECK")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/health")
    result = response.json()
    
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("🔐 ANTI-SPOOFING FRAUD DETECTION - API TESTS")
    print("=" * 50)
    
    try:
        test_health()
        test_legitimate_claim()
        test_suspicious_claim()
        test_fraud_ring()
        test_user_claims()
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 50 + "\n")
    
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server.")
        print("Make sure the Flask app is running: python app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")