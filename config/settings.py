# Configuration settings for patient monitoring system
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure settings
EVENTHUB_CONNECTION_STRING = os.getenv("EVENTHUB_CONNECTION_STRING", "")
EVENTHUB_NAME = os.getenv("EVENTHUB_NAME", "patient-vitals-hub")
STORAGE_CONNECTION_STRING = os.getenv("STORAGE_CONNECTION_STRING", "")
STORAGE_CONTAINER_NAME = os.getenv("STORAGE_CONTAINER_NAME", "patient-data")

# Vital sign normal ranges
VITAL_RANGES = {
    "heart_rate": {
        "min": 60,
        "max": 100,
        "critical_min": 40,
        "critical_max": 130,
    },
    "temperature": {
        "min": 36.0,
        "max": 37.5,
        "critical_min": 35.0,
        "critical_max": 38.5,
    },
    "oxygen_saturation": {
        "min": 95,
        "max": 100,
        "critical_min": 90,
        "critical_max": 100,
    },
    "respiratory_rate": {
        "min": 12,
        "max": 20,
        "critical_min": 10,
        "critical_max": 25,
    },
    "blood_pressure_systolic": {
        "min": 90,
        "max": 120,
        "critical_min": 80,
        "critical_max": 180,
    },
    "blood_pressure_diastolic": {
        "min": 60,
        "max": 80,
        "critical_min": 50,
        "critical_max": 110,
    },
}

# Alert settings
ALERT_LEVELS = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4
}

# Logging settings
LOG_FILE = os.getenv("LOG_FILE", "patient_alerts.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Simulation settings
SIMULATION_PATIENT_COUNT = int(os.getenv("SIMULATION_PATIENT_COUNT", "5"))
SIMULATION_INTERVAL_SECONDS = float(os.getenv("SIMULATION_INTERVAL_SECONDS", "1.0"))
ANOMALY_PROBABILITY = float(os.getenv("ANOMALY_PROBABILITY", "0.1")) 