#!/usr/bin/env python3
"""
Simple test script to verify configuration settings are loaded correctly.
This tests that environment variables are properly loaded from the .env file.
"""

import os
import sys
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    EVENTHUB_CONNECTION_STRING,
    EVENTHUB_NAME,
    STORAGE_CONNECTION_STRING,
    STORAGE_CONTAINER_NAME,
    SIMULATION_PATIENT_COUNT,
    SIMULATION_INTERVAL_SECONDS,
    ANOMALY_PROBABILITY,
    LOG_FILE,
    LOG_LEVEL,
    VITAL_RANGES,
    ALERT_LEVELS
)

def test_config():
    """Test configuration settings are loaded correctly."""
    print("Testing configuration settings...")
    
    # Check Azure settings
    print("\nAzure Settings:")
    print(f"  EVENTHUB_NAME: {EVENTHUB_NAME}")
    print(f"  EVENTHUB_CONNECTION_STRING: {'<set>' if EVENTHUB_CONNECTION_STRING else '<not set>'}")
    print(f"  STORAGE_CONTAINER_NAME: {STORAGE_CONTAINER_NAME}")
    print(f"  STORAGE_CONNECTION_STRING: {'<set>' if STORAGE_CONNECTION_STRING else '<not set>'}")
    
    # Check simulation settings
    print("\nSimulation Settings:")
    print(f"  SIMULATION_PATIENT_COUNT: {SIMULATION_PATIENT_COUNT}")
    print(f"  SIMULATION_INTERVAL_SECONDS: {SIMULATION_INTERVAL_SECONDS}")
    print(f"  ANOMALY_PROBABILITY: {ANOMALY_PROBABILITY}")
    
    # Check logging settings
    print("\nLogging Settings:")
    print(f"  LOG_FILE: {LOG_FILE}")
    print(f"  LOG_LEVEL: {LOG_LEVEL}")
    
    # Verify vital ranges are loaded
    print("\nVital Ranges:")
    for vital, ranges in VITAL_RANGES.items():
        print(f"  {vital}: min={ranges['min']}, max={ranges['max']}")
    
    # Verify alert levels are loaded
    print("\nAlert Levels:")
    for level, value in ALERT_LEVELS.items():
        print(f"  {level}: {value}")
    
    print("\nConfiguration test complete!")
    print("If you see actual values above, your configuration is working correctly.")
    print("If you see empty or default values, check your .env file.")

if __name__ == "__main__":
    test_config() 