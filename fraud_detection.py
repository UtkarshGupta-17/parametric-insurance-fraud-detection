import numpy as np
from datetime import datetime
from sklearn.ensemble import IsolationForest
from data_validator import DataValidator
from config import Config

class FraudDetector:
    """AI/ML Fraud Detection Layer"""
    
    def __init__(self):
        self.validator = DataValidator()
        self.claims_history = Config.CLAIMS_HISTORY
        # Initialize Isolation Forest for anomaly detection
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.model_trained = False
    
    # ============ BEHAVIORAL MODELING ============
    def detect_trajectory_anomaly(self, gps_history):
        """Detect unrealistic movement patterns"""
        if len(gps_history) < 2:
            return 0.1
        
        anomaly_score = 0
        for i in range(1, len(gps_history)):
            prev = gps_history[i-1]
            curr = gps_history[i]
            
            # Check for teleportation (too far in too short time)
            distance = self.validator.calculate_distance(
                prev['lat'], prev['lon'], 
                curr['lat'], curr['lon']
            )
            time_diff = (curr['timestamp'] - prev['timestamp']) / 60  # minutes
            
            if time_diff > 0 and (distance / time_diff) > 100:  # >100 km/min
                anomaly_score += 0.5
        
        return min(anomaly_score / len(gps_history), 0.9)
    
    def detect_perfect_straight_path(self, gps_history):
        """Detect unnaturally straight paths (GPS spoofing indicator)"""
        if len(gps_history) < 3:
            return 0.1
        
        # Calculate variance in direction changes
        directions = []
        for i in range(1, len(gps_history)):
            lat_diff = gps_history[i]['lat'] - gps_history[i-1]['lat']
            lon_diff = gps_history[i]['lon'] - gps_history[i-1]['lon']
            directions.append((lat_diff, lon_diff))
        
        # Very low variance = suspicious
        if len(directions) > 2:
            direction_variance = np.var(directions)
            if direction_variance < 0.0001:
                return 0.8  # Very straight path = suspicious
        
        return 0.1
    
    def check_historical_patterns(self, user_id, current_claim):
        """Learn and detect deviations from user patterns"""
        if user_id not in self.claims_history:
            return 0.2  # New user
        
        user_claims = self.claims_history[user_id]
        if len(user_claims) < 3:
            return 0.2  # Not enough history
        
        # Calculate average claim characteristics
        avg_claims_per_hour = len(user_claims) / 24  # Simplified
        avg_duration = np.mean([c.get('duration', 0) for c in user_claims])
        
        # Check deviation
        current_duration = current_claim.get('duration', 0)
        if abs(current_duration - avg_duration) > avg_duration * 2:
            return 0.4  # Significant deviation
        
        return 0.1
    
    # ============ ANOMALY DETECTION ============
    def detect_anomaly_isolation_forest(self, features):
        """Use Isolation Forest for anomaly detection"""
        try:
            # Normalize features
            X = np.array([features])
            prediction = self.anomaly_detector.predict(X)
            
            # -1 = anomaly, 1 = normal
            if prediction[0] == -1:
                return 0.7
            return 0.1
        except:
            return 0.2
    
    def detect_too_perfect_gps(self, gps_accuracy, signal_quality):
        """Real GPS has noise; perfect signals indicate spoofing"""
        if signal_quality > 0.98:
            return 0.8  # Too perfect
        if gps_accuracy < 5:
            return 0.6  # Unrealistically accurate
        return 0.1
    
    # ============ FRAUD RING DETECTION ============
    def detect_fraud_ring(self, user_id, ip_address, device_id, region, timestamp):
        """Graph-based fraud ring detection"""
        fraud_ring_score = 0
        
        # Check shared IP
        ip_score = self.validator.validate_ip_sharing(ip_address, user_id)
        fraud_ring_score += ip_score * 0.4
        
        # Check synchronized claims
        sync_score = self.validator.validate_synchronized_claims(timestamp, region)
        fraud_ring_score += sync_score * 0.3
        
        # Check device sharing
        device_share_count = 0
        for uid, claims in self.claims_history.items():
            if uid != user_id:
                for claim in claims:
                    if claim.get('device_id') == device_id:
                        device_share_count += 1
        
        if device_share_count > 3:
            fraud_ring_score += 0.3
        
        return min(fraud_ring_score, 0.9)
    
    def extract_features_for_ml(self, claim_data):
        """Extract features for ML model"""
        features = [
            claim_data.get('gps_accuracy', 50),
            claim_data.get('signal_quality', 0.8),
            claim_data.get('accelerometer_data', 0.5),
            claim_data.get('battery_drain', 5),
            claim_data.get('app_foreground_time', 50),
            claim_data.get('latency_ms', 100),
        ]
        return features