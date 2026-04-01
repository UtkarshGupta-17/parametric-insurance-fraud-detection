from flask import Flask, request, jsonify
from datetime import datetime
from risk_scorer import RiskScorer
from config import Config
from data_validator import DataValidator

app = Flask(__name__)
app.config.from_object(Config)

# Initialize components
risk_scorer = RiskScorer()
validator = DataValidator()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'OK', 'message': 'Server is running'}), 200

@app.route('/submit-claim', methods=['POST'])
def submit_claim():
    """
    Submit insurance claim for fraud verification
    
    Request body example:
    {
        "user_id": "user123",
        "claim_amount": 500,
        "region": "downtown_area",
        "gps_accuracy": 25,
        "signal_quality": 0.92,
        "accelerometer_data": 0.8,
        "battery_drain": 8,
        "app_foreground_time": 75,
        "latency_ms": 45,
        "device_id": "device_abc123",
        "ip_address": "192.168.1.100",
        "duration": 15,
        "gps_history": [
            {"lat": 40.7128, "lon": -74.0060, "timestamp": 1234567890},
            {"lat": 40.7129, "lon": -74.0061, "timestamp": 1234567950}
        ],
        "curr_location": {"lat": 40.7129, "lon": -74.0061},
        "prev_location": {"lat": 40.7128, "lon": -74.0060},
        "time_diff_minutes": 1,
        "gps_movement": 0.15
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'claim_amount', 'device_id', 'ip_address']
        if not all(field in data for field in required_fields):
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {required_fields}'
            }), 400
        
        # Add timestamp if not provided
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().timestamp()
        
        # Get last claim timestamp
        user_id = data['user_id']
        last_claim = None
        if user_id in validator.claims_history:
            if validator.claims_history[user_id]:
                last_claim = validator.claims_history[user_id][-1].get('timestamp')
        
        data['last_claim_timestamp'] = last_claim
        
        # Compute risk score
        risk_scores = risk_scorer.compute_final_risk_score(data)
        final_score = risk_scores['final_score']
        
        # Get risk level and recommendation
        risk_level = risk_scorer.get_risk_level(final_score)
        recommendation = risk_scorer.get_recommendation(risk_level)
        
        # Store claim in history
        if user_id not in validator.claims_history:
            validator.claims_history[user_id] = []
        
        validator.claims_history[user_id].append({
            'timestamp': data['timestamp'],
            'device_id': data.get('device_id'),
            'ip_address': data.get('ip_address'),
            'region': data.get('region'),
            'duration': data.get('duration', 0)
        })
        
        # Prepare response
        response = {
            'status': 'success',
            'claim_id': f"CLAIM_{user_id}_{int(data['timestamp'])}",
            'user_id': user_id,
            'claim_amount': data.get('claim_amount'),
            'risk_assessment': {
                'final_risk_score': final_score,
                'risk_level': risk_level,
                'recommendation': recommendation,
                'breakdown': {
                    'location_risk': risk_scores['location_risk'],
                    'device_risk': risk_scores['device_risk'],
                    'behavior_risk': risk_scores['behavior_risk'],
                    'network_risk': risk_scores['network_risk'],
                    'history_risk': risk_scores['history_risk']
                }
            },
            'action': {
                'type': 'INSTANT_PAYOUT' if risk_level == 'LOW' else (
                    'DELAYED_PAYOUT' if risk_level == 'MEDIUM' else 'MANUAL_REVIEW'
                ),
                'message': recommendation
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error processing claim: {str(e)}'
        }), 500

@app.route('/claim-status/<claim_id>', methods=['GET'])
def check_claim_status(claim_id):
    """Check status of a submitted claim"""
    try:
        return jsonify({
            'claim_id': claim_id,
            'status': 'processed',
            'message': 'Claim processing complete. Check submit-claim response for details.'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/user-claims/<user_id>', methods=['GET'])
def get_user_claims(user_id):
    """Get all claims for a user"""
    try:
        if user_id not in validator.claims_history:
            return jsonify({
                'user_id': user_id,
                'total_claims': 0,
                'claims': []
            }), 200
        
        claims = validator.claims_history[user_id]
        return jsonify({
            'user_id': user_id,
            'total_claims': len(claims),
            'claims': claims
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/fraud-ring-check', methods=['POST'])
def check_fraud_ring():
    """Check for fraud ring activity"""
    try:
        data = request.get_json()
        
        fraud_ring_score = risk_scorer.detector.detect_fraud_ring(
            data.get('user_id'),
            data.get('ip_address'),
            data.get('device_id'),
            data.get('region'),
            data.get('timestamp', datetime.now().timestamp())
        )
        
        return jsonify({
            'fraud_ring_detected': fraud_ring_score > 0.5,
            'fraud_ring_score': round(fraud_ring_score, 3),
            'severity': 'HIGH' if fraud_ring_score > 0.7 else (
                'MEDIUM' if fraud_ring_score > 0.5 else 'LOW'
            )
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Anti-Spoofing Fraud Detection System Started")
    print("📊 Endpoints Available:")
    print("   POST   /submit-claim - Submit claim for verification")
    print("   GET    /claim-status/<claim_id> - Check claim status")
    print("   GET    /user-claims/<user_id> - Get user's claims")
    print("   POST   /fraud-ring-check - Detect fraud rings")
    print("   GET    /health - Health check")
    print("\n🔗 API running on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)