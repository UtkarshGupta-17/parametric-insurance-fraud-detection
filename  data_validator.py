import math
from datetime import datetime
from config import Config

class DataValidator:
    """Multi-signal verification layer"""
    
    def __init__(self):
        self.claims_history = Config.CLAIMS_HISTORY
    
    # ============ LOCATION & NETWORK VALIDATION ============
    def validate_gps_accuracy(self, gps_accuracy):
        """Check if GPS accuracy is reasonable"""
        if gps_accuracy is None:
            return 0.5  # Moderate risk if no accuracy data
        
        if gps_accuracy > Config.GPS_ACCURACY_THRESHOLD:
            return 0.8  # High risk - poor accuracy suggests spoofing
        return 0.1  # Low risk - good accuracy
    
    def validate_gps_consistency(self, gps_signal_quality):
        """Check if GPS signal is too perfect (unusual pattern)"""
        # Real GPS has natural drift/noise
        if gps_signal_quality > 0.99:
            return 0.7  # Suspicious - unnaturally perfect
        if gps_signal_quality < 0.5:
            return 0.6  # Weak signal - unreliable
        return 0.1  # Normal
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two GPS coordinates in km"""
        R = 6371  # Earth's radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c
    
    def validate_speed(self, prev_lat, prev_lon, curr_lat, curr_lon, time_diff_minutes):
        """Check if movement speed is realistic"""
        if time_diff_minutes == 0:
            return 0.1
        
        distance_km = self.calculate_distance(prev_lat, prev_lon, curr_lat, curr_lon)
        speed_kmh = (distance_km / time_diff_minutes) * 60
        
        if speed_kmh > Config.REALISTIC_SPEED * 2:  # Teleportation
            return 0.9  # Very suspicious
        if speed_kmh > Config.REALISTIC_SPEED:
            return 0.4  # Slightly suspicious
        return 0.1  # Normal
    
    def validate_network_latency(self, latency_ms, claimed_region):
        """Verify latency matches claimed region"""
        # Simple validation: latency should be reasonable for region
        if latency_ms > 200:
            return 0.5  # Could indicate wrong region
        return 0.1
    
    # ============ DEVICE & SENSOR ANALYSIS ============
    def validate_sensor_gps_consistency(self, accelerometer_data, gps_movement):
        """Cross-validate sensor data with GPS movement"""
        if not accelerometer_data:
            return 0.3  # No sensor data available
        
        # If sensors show no movement but GPS shows movement = suspicious
        if accelerometer_data < 0.1 and gps_movement > 5:
            return 0.8  # Likely spoofing
        
        if abs(accelerometer_data - gps_movement) > 0.5:
            return 0.5  # Mismatch detected
        return 0.1
    
    def validate_device_fingerprint(self, device_id, user_id):
        """Check if device is consistent with user history"""
        if user_id not in self.claims_history:
            return 0.2  # New user
        
        user_devices = [claim['device_id'] for claim in self.claims_history[user_id]]
        
        if device_id not in user_devices:
            return 0.4  # New device (slightly suspicious)
        return 0.1
    
    def validate_battery_usage(self, battery_drain_percent, claim_duration_minutes):
        """Check if battery usage is realistic"""
        expected_drain = (claim_duration_minutes / 60) * 5  # ~5% per hour
        
        if battery_drain_percent == 0 and claim_duration_minutes > 10:
            return 0.7  # No battery drain while claiming activity = suspicious
        
        if battery_drain_percent > expected_drain * 2:
            return 0.3  # High drain (but could be legitimate)
        return 0.1
    
    def validate_app_activity(self, app_foreground_time_percent):
        """Check if delivery app was active during claim"""
        if app_foreground_time_percent < 20:
            return 0.6  # App not actively used
        if app_foreground_time_percent < 50:
            return 0.3  # Somewhat used
        return 0.1
    
    # ============ ENVIRONMENTAL VALIDATION ============
    def validate_timestamp_consistency(self, claim_timestamp, last_claim_timestamp):
        """Check if timestamp is reasonable"""
        if last_claim_timestamp is None:
            return 0.1
        
        time_diff = abs(claim_timestamp - last_claim_timestamp)
        
        if time_diff < 60:  # Claims within 1 minute
            return 0.8  # Suspicious pattern
        if time_diff < 300:  # Claims within 5 minutes
            return 0.5  # Somewhat suspicious
        return 0.1
    
    def validate_weather_correlation(self, claimed_weather, region):
        """Check if weather matches claimed region (simplified)"""
        # In production, call weather API
        # For now, simple check
        if claimed_weather and claimed_weather not in ['clear', 'cloudy', 'rainy', 'snow']:
            return 0.5
        return 0.1
    
    # ============ NETWORK ANOMALIES ============
    def validate_ip_sharing(self, ip_address, user_id):
        """Check if IP is shared with many users (fraud ring indicator)"""
        if user_id not in self.claims_history:
            return 0.1
        
        other_users_same_ip = 0
        for uid, claims in self.claims_history.items():
            if uid != user_id:
                for claim in claims:
                    if claim.get('ip_address') == ip_address:
                        other_users_same_ip += 1
        
        if other_users_same_ip > 5:
            return 0.9  # Strong fraud ring indicator
        if other_users_same_ip > 2:
            return 0.6
        return 0.1
    
    def validate_synchronized_claims(self, timestamp, region):
        """Check if many claims happening simultaneously in same region"""
        synchronized_count = 0
        for claims in self.claims_history.values():
            for claim in claims:
                time_diff = abs(claim.get('timestamp', 0) - timestamp)
                same_region = claim.get('region') == region
                
                if time_diff < 120 and same_region:  # Within 2 minutes, same region
                    synchronized_count += 1
        
        if synchronized_count > 10:
            return 0.9  # Coordinated fraud likely
        if synchronized_count > 5:
            return 0.6
        return 0.1