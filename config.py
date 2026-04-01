# Configuration settings for Parametric Insurance Fraud Detection

# Risk thresholds
RISK_THRESHOLDS = {
    'low': 0.2,
    'medium': 0.5,
    'high': 0.8
}

# Weights for the model
WEIGHTS = {
    'feature1': 0.3,
    'feature2': 0.5,
    'feature3': 0.2
}

# GPS validation parameters
GPS_VALIDATION = {
    'latitude_tolerance': 0.01,
    'longitude_tolerance': 0.01,
    'valid_range': {
        'min_latitude': -90,
        'max_latitude': 90,
        'min_longitude': -180,
        'max_longitude': 180
    }
}

# Claims history parameters
CLAIMS_HISTORY = {
    'years_back': 5,
    'max_claim_amount': 100000,  # Maximum claim amount over the history
    'required_documents': ['claim_form', 'identity_proof', 'location_proof']
}