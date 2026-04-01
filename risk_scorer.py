from config import Config
from fraud_detection import FraudDetector
from data_validator import DataValidator
from datetime import datetime

class RiskScorer:
    """Dynamic Risk Scoring Engine"""
    
    def __init__(self):
        self.detector = FraudDetector()
        self.validator = DataValidator()
        self.config = Config
    
    def compute_location_risk(self, claim_data):
        """Location & Network risk score"""
        score = 0
        
        # GPS accuracy
        score += self.validator.validate_gps_accuracy(
            claim_data.get('gps_accuracy')
        ) * 0.3
        
        # GPS consistency
        score += self.validator.validate_gps_consistency(
            claim_data.get('signal_quality', 0.8)
        ) * 0.3
        
        # Speed validation
        if 'prev_location' in claim_data and 'curr_location' in claim_data:
            prev = claim_data['prev_location']
            curr = claim_data['curr_location']
            time_diff = claim_data.get('time_diff_minutes', 1)
            
            score += self.validator.validate_speed(
                prev['lat'], prev['lon'],
                curr['lat'], curr['lon'],
                time_diff
            ) * 0.2
        
        # Network latency
        score += self.validator.validate_network_latency(
            claim_data.get('latency_ms', 50),
            claim_data.get('region')
        ) * 0.2
        
        return min(score / 4, 1.0)
    
    def compute_device_risk(self, claim_data):
        """Device & Sensor risk score"""
        score = 0
        
        # Sensor-GPS consistency
        score += self.validator.validate_sensor_gps_consistency(
            claim_data.get('accelerometer_data', 0),
            claim_data.get('gps_movement', 0)
        ) * 0.3
        
        # Device fingerprint
        score += self.validator.validate_device_fingerprint(
            claim_data.get('device_id'),
            claim_data.get('user_id')
        ) * 0.3
        
        # Battery usage
        score += self.validator.validate_battery_usage(
            claim_data.get('battery_drain', 5),
            claim_data.get('duration', 10)
        ) * 0.2
        
        # App activity
        score += self.validator.validate_app_activity(
            claim_data.get('app_foreground_time', 50)
        ) * 0.2
        
        return min(score / 4, 1.0)
    
    def compute_behavior_risk(self, claim_data):
        """Behavioral risk score"""
        score = 0
        
        # Trajectory anomaly
        gps_history = claim_data.get('gps_history', [])
        score += self.detector.detect_trajectory_anomaly(gps_history) * 0.3
        
        # Perfect straight path
        score += self.detector.detect_perfect_straight_path(gps_history) * 0.3
        
        # Historical patterns
        score += self.detector.check_historical_patterns(
            claim_data.get('user_id'),
            claim_data
        ) * 0.2
        
        # Timestamp consistency
        score += self.validator.validate_timestamp_consistency(
            claim_data.get('timestamp', datetime.now().timestamp()),
            claim_data.get('last_claim_timestamp')
        ) * 0.2
        
        return min(score / 4, 1.0)
    
    def compute_network_risk(self, claim_data):
        """Network & Fraud Ring risk"""
        score = 0
        
        # IP sharing
        score += self.validator.validate_ip_sharing(
            claim_data.get('ip_address'),
            claim_data.get('user_id')
        ) * 0.5
        
        # Synchronized claims
        score += self.validator.validate_synchronized_claims(
            claim_data.get('timestamp', datetime.now().timestamp()),
            claim_data.get('region')
        ) * 0.5
        
        return min(score / 2, 1.0)
    
    def compute_history_risk(self, claim_data):
        """User history risk"""
        user_id = claim_data.get('user_id')
        
        # New users have slightly higher risk
        if user_id not in self.validator.claims_history:
            return 0.3
        
        user_claims = self.validator.claims_history[user_id]
        
        # Fraud ring detection
        fraud_ring_risk = self.detector.detect_fraud_ring(
            user_id,
            claim_data.get('ip_address'),
            claim_data.get('device_id'),
            claim_data.get('region'),
            claim_data.get('timestamp', datetime.now().timestamp())
        )
        
        return fraud_ring_risk
    
    def compute_final_risk_score(self, claim_data):
        """Compute weighted final risk score"""
        location_risk = self.compute_location_risk(claim_data)
        device_risk = self.compute_device_risk(claim_data)
        behavior_risk = self.compute_behavior_risk(claim_data)
        network_risk = self.compute_network_risk(claim_data)
        history_risk = self.compute_history_risk(claim_data)
        
        # Weighted combination
        final_score = (
            location_risk * self.config.LOCATION_WEIGHT +
            device_risk * self.config.DEVICE_WEIGHT +
            behavior_risk * self.config.BEHAVIOR_WEIGHT +
            network_risk * self.config.NETWORK_WEIGHT +
            history_risk * self.config.HISTORY_WEIGHT
        )
        
        return {
            'final_score': round(final_score, 3),
            'location_risk': round(location_risk, 3),
            'device_risk': round(device_risk, 3),
            'behavior_risk': round(behavior_risk, 3),
            'network_risk': round(network_risk, 3),
            'history_risk': round(history_risk, 3),
        }
    
    def get_risk_level(self, risk_score):
        """Classify risk level"""
        if risk_score < self.config.LOW_RISK_THRESHOLD:
            return 'LOW'
        elif risk_score < self.config.MEDIUM_RISK_THRESHOLD:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def get_recommendation(self, risk_level):
        """Get action recommendation"""
        recommendations = {
            'LOW': 'Instant Payout - Legitimate claim',
            'MEDIUM': 'Delayed Payout - Soft verification required',
            'HIGH': 'Manual Review - Flagged for fraud investigation'
        }
        return recommendations.get(risk_level, 'Unknown')